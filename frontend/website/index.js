const express = require("express");
const path    = require("path");

const app = express();

app.get("/", function(req, res) {
    res.sendFile(path.join(__dirname, 'html/home.html'));
})

app.get("/compra", function(req, res) {
    res.sendFile(path.join(__dirname, 'html/compra.html'));
})

app.listen(2020, "25.80.62.167");
