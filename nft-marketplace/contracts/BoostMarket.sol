// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

// Interface for the accepted currency types
// https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol
interface InterfaceERC721 {

    // Transfer function
    function transferFrom(address from, address to, uint256 tokenId) external;
}


// Main Market Contract
contract BoostMarket {

    // Status Codes
    enum Statuses {
        Active, 
        Sold,
        Cancelled
    }

    // Listing Data Structure
    struct Listing {
        Statuses status; 
        address seller;
        address token;
        uint tokenId;
        uint price; 
    }

    // Current index of listing
    uint private _listingId = 0;
    mapping(uint => Listing) private _listings; // Private variables are prefixed with _


    /*
        Free Methods : Do not write into the network
    */
    function getTokenListingItem(uint listingId) public view 
    returns (Listing memory){
        return _listings[listingId];
    }
    
    // Create Token Listing
    function createTokenListing(address token, uint tokenId, uint price) external {

        // ERC721 support - transfer
        // noqa
        InterfaceERC721(token).transferFrom(
            msg.sender, // Seller of the token
            address(this), // Address of the company, harvested through the object.
            tokenId
        );        


        // Listing storage object
        Listing memory listing = Listing(
            Statuses.Active, // Set the initial status to "Active"
            msg.sender, // Get the seller id 
            token,
            tokenId,
            price
        );

        // Adding the listing object to the mapping
        _listingId ++;
        _listings[_listingId] = listing;
    }

    // Buy Token with ID
    function buyTokenListing(uint listingId) external payable{

        // Get the relevant listing 
        Listing storage listing = _listings[listingId]; // https://ethereum.stackexchange.com/questions/1232/difference-between-memory-and-storage

        // Check status of the listing
        if (listing.status != Statuses.Active){

            // Cancel transaction
            revert(
                "This item is not active."
            );
        } 

        // Ensure that the seller is not the buyer
        if (msg.sender != listing.seller) {

            // Cancel transaction
            revert(
                "The seller can not be the buyer."
            );
        }

        // Ensure that the amount pledged for the listing is equal to the price of the listing
        // https://www.investopedia.com/terms/w/wei.asp
        if (msg.value != listing.price) {

            // Cancel transaction
            revert(
                "The amount pledged is not equal to the price of the listing."
            );
        }
        
        // Change the status of the listing
        listing.status = Statuses.Sold;
        
        
        InterfaceERC721(listing.token).transferFrom(
            address(this), // Address of the seller, harvested through the object.
            msg.sender,
            listing.tokenId
        );
        
        payable(listing.seller).transfer(listing.price);
    }

    // Function to remove a listing
    function removeTokenListing(uint listingId) public {

        // Get listing instance
        Listing storage listing = _listings[listingId];

        // Check status of the listing
        if (listing.status != Statuses.Active){

            // Cancel transaction
            revert(
                "This item is not active."
            );
        } 

        // Ensure that only the seller can remove a listing
        if (msg.sender != listing.seller) {

            // Cancel transaction
            revert(
                "Only the seller can remove their listings."
            );
        }

        // Change the status of the listing
        listing.status = Statuses.Cancelled;

        InterfaceERC721(listing.token).transferFrom(
            address(this), // Address of the seller, harvested through the object.
            msg.sender,
            listing.tokenId
        );

    }
}

