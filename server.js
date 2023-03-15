const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

// const PORT = process.env.PORT;
const PORT = 8080;

var username = ""; // username of TDSQL-C SQL database default: root
var password = ""; // password of TDSQL-C SQL database
var host = ""; // host name of TDSQL-C SQL database
var port = ""; // port number of TDSQL-C SQL database
var database = ""; // database name of TDSQL-C SQL database

app.get("/", function (req, res) {
  res.send(`Server is working on ${PORT}`);
});

app.post("/login", async function (req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST");
  res.setHeader(
    "Access-Control-Allow-Headers",
    "X-Requested-With,Content-Type"
  );

  username = req.body.username;
  password = req.body.password;
  host = req.body.host;
  port = req.body.port;
  database = req.body.database;

  try {
    const mysql = require("mysql");
    // set authentication to database
    const connection = mysql.createConnection({
      host: host,
      port: port,
      database: database,
      user: username,
      password: password,
    });

    //connect to database
    await connection.connect();

    res.json("login done");

    connection.end();
  } catch (error) {
    console.log("***error****\n", error);
  }
});

app.get("/getAllList", function (req, res) {
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Access-Control-Allow-Origin", "*");

  const mysql = require("mysql");

  // set authentication to database
  const connection = mysql.createConnection({
    host: host,
    port: port,
    database: database,
    user: username,
    password: password,
  });

  console.log("*****get All list*****\n");

  //connect to database
  connection.connect();

  //set query SQL
  connection.query(
    "SELECT * FROM restaurants",
    function (error, results, fields) {
      if (error) {
        console.log("******error*********\n", error);
        connection.end();
        return;
      }

      //return searched results to response
      res.json(results);
    }
  );

  //end database connection
  connection.end();
});

app.post("/insertData", function (req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST");
  res.setHeader(
    "Access-Control-Allow-Headers",
    "X-Requested-With,Content-Type"
  );
  let query = req.body.query;

  console.log("*****insertData parameter*****\n", query);

  const mysql = require("mysql");

  // set authentication to database
  const connection = mysql.createConnection({
    host: host,
    port: port,
    database: database,
    user: username,
    password: password,
  });

  //connect to database
  connection.connect();

  //set query SQL
  connection.query(query, function (error, results, fields) {
    if (error) {
      console.log("******error*********\n", error);
      connection.end();
      res.json("error");
      return;
    }

    //return searched results to response
    res.json(results);
  });
});

app.get("/getTencentAccounts", function (req, res) {
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Access-Control-Allow-Origin", "*");

  tencentGetAccounts(req, res);
});

app.get("/test", function (req, res) {
  // res.send(req.params);
  res.json("return value from test by get method");
});

app.post("/IoTTest", function (req, res) {
  let data = "req body value ";
  res.send(data + req.body);
  res.json(data + req.body.data);
});

function tencentGetAccounts(req, res) {
  //set tencent parameters
  // Depends on tencentcloud-sdk-nodejs version 4.0.3 or higher
  const tencentcloud = require("tencentcloud-sdk-nodejs");
  const CynosdbClient = tencentcloud.cynosdb.v20190107.Client;

  //parameters
  var region = "";
  var endpoint = "";

  var data = "not fetched data";

  // 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
  // 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
  // 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
  var clientConfig = {
    credential: {
      secretId: "secretId",
      secretKey: "secretKey",
    },
    region: region,
    profile: {
      httpProfile: {
        endpoint: endpoint,
      },
    },
  };
  region = req.query.region;
  endpoint = req.query.endpoint;
  console.log("request parameters", region, endpoint);

  clientConfig.region = region;
  clientConfig.profile.httpProfile.endpoint = endpoint;

  // 实例化要请求产品的client对象,clientProfile是可选的
  var client = new CynosdbClient(clientConfig);
  var params = {
    ClusterId: req.query.ClusterId,
  };

  client.SearchClusterTables(params).then(
    (response) => {
      data = response;
      res.json(data);
    },
    (err) => {
      console.error("error", err);
      res.json(err);
    }
  );
}

//monitor server
app.listen(PORT, function (req, res) {
  console.log(`Kinsta Server is running on port ${PORT}`);
});

// var http = require("http");

// http
//   .createServer(function (req, res) {
//     var html = buildHtml(req);

//     res.writeHead(200, {
//       "Content-Type": "text/html",
//       "Content-Length": html.length,
//       Expires: new Date().toUTCString(),
//     });
//     res.end(html);
//   })
//   .listen(PORT);

// function buildHtml(req) {
//   var header = "Hello World!";
//   var body = "This is html created by nodejs and run by node server.js command";

//   // concatenate header string
//   // concatenate body string

//   return (
//     "<!DOCTYPE html>" +
//     "<html><head>" +
//     header +
//     "</head><body>" +
//     body +
//     "</body></html>"
//   );
// }
