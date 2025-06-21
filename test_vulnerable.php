<?php
// Test file with various vulnerabilities for Web2Static testing

// SQL Injection vulnerability
$user_id = $_GET['id'];
$query = "SELECT * FROM users WHERE id = " . $user_id;
mysql_query($query);

// XSS vulnerability
echo "Hello " . $_GET['name'];

// Command injection
$cmd = $_POST['command'];
system("ls -la " . $cmd);

// Path traversal
$file = $_GET['file'];
include($file);

// Hardcoded credentials
$password = "supersecret123";
$api_key = "sk-1234567890abcdef1234567890abcdef";

// Weak random
$token = rand();

// Weak crypto
$hash = md5($password);

// Safe code (should not trigger)
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$user_id]);
?>
