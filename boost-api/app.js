const ipfs_client = require('ipfs-http-client');
const express = require('express');
const body_parser = require('body-parser');
const file_upload = require('express-fileupload');
const fs = require('fs');
const mysql = require("mysql");
const bodyParser = require("body-parser");


const ipfs = ipfs_client.create({
    host: 'localhost',
    port: '5001',
    protocol : 'http'
});

const app = express();
app.set('view engine', 'ejs');
app.use(body_parser.urlencoded({
    extended: true
}));
app.use(file_upload());

const addFile = async ( fileName, filePath ) => {
    try{
            const file = fs.readFileSync(filePath);
            let results = [];
            const fileAdded = await ipfs.add({path: fileName, content: file});
            return fileHash = fileAdded.cid; 
        }
        
    
    catch (error){
        console.log(error);
        return null;
    }
}



// Root API Call
app.get("/", (req,res) => {
    res.send("API up and running");
});

// Upload file API Call
app.post("/upload", (req,res) => {
    let file = req.files.file;
    let file_name = req.body.file_name;
    let file_path = "files/" + file_name;

    console.log(file_path);

    // Download file to server


        file.mv(file_path, async (err) => {
        if (err) {
            console.log("Download Failure");
            return res.status(500).send(err);
        }

        let file_hash = await addFile(file_name, file_path);
        fs.unlink(file_path, (err) => {
            if (err){
                console.log("File Hash error");
                return res.status(501).send(err);
            }
        });

        console.log(file_hash);
        let url = "https://ipfs.io/ipfs/" + file_hash 

        res.send(
            {
                "url" : url
            }
        );
    });
});

// MySQL setup

var passwordRoot = "Courier1@";
database = "boost";

var con = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: passwordRoot,
    database: database
})

con.connect(function (err) {
    if (err) console.log(err);
});

app.use(bodyParser.json());

// Add new location
app.post("/addmapelement", (req,res) => {
    let lat = req.body.latitude;
    let long = req.body.longitude;
    let addr = req.body.address;
    let name = req.body.name;
    let desc = req.body.description;
    let special = req.body.special;

    
    let sql = `INSERT INTO boost.shop (latitude,longitude,address,bname,bdesc,special) VALUES (?,?,?,?,?,?);`;
    console.log(sql);

    con.query(
        sql,
        [
            lat,                                                                          
            long,
            addr,
            name,
            desc,
            special
        ],
        function (err, response) {
            if (err) 
            {
                console.log(err);
                res.status(501).send(err);
                return;
            }
            res.json(response);
        }
    );
});

app.get("/getlocations", (req,res) => {
    let sql = `SELECT * FROM boost.shop`;
    con.query(sql, function(err,response) {
        if(err)
        {
            console.log(err);
            res.status(501).send(err);
            return;
        }
        res.json(response);
    })
}); 

app.get("/getaddresses", (req,res) => {
    let sql = `SELECT address FROM boost.shop WHERE address IS NOT NULL;`;
    con.query(sql, function(err,response) {
        if(err)
        {
            console.log(err);
            res.status(501).send(err);
            return;
        }
        res.json(response);
    })
})



app.listen(3000);