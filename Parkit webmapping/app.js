const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const { Pool } = require("pg");

const app = express();
const port = 3000;

app.use(cors()); // Enable CORS

app.use(express.static("public"));

app.set("views", __dirname + "/views");
app.set("view engine", "ejs");

app.use(bodyParser.json());

const pool = new Pool({
  user: "postgres",
  host: "localhost",
  database: "ParkitDB",
  password: "root",
  port: 5432,
});

app.get("/", (req, res) => {
  res.render("index");
});

app.get("/search", async (req, res) => {
  res.render("search");
});


app.get("/getPoints", async (req, res) => {
  try {
    const client = await pool.connect();
    const result = await client.query("SELECT * FROM point");
    const data = result.rows;
    res.json(data);
    client.release();
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal Server Error" });
  }
});


app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});