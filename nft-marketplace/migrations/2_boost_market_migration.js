// Deployed smartcontract
const BoostMarket = artifacts.require("BoostMarket");


module.exports = function (deployer) {
    deployer.deploy(BoostMarket);
}