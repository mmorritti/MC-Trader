const http = require("http")
const fs   = require("fs")


const port = 2020


const server = http.createServer(function(req, res) {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    fs.readFile("html/index.html", function(error, data) {
        if (error) {
            res.writeHead(404);
            console.log("Error 404");
        } 
        else {
            res.write(data);
        }

        res.end();
    })
})

server.listen(port, "25.80.62.167");
