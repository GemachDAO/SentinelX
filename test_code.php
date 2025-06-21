<?php
// Test vulnerable PHP code for workflow testing
$user_input = $_GET['input'];

// SQL Injection vulnerability
$query = "SELECT * FROM users WHERE name = '" . $user_input . "'";
$result = mysql_query($query);

// XSS vulnerability
echo "<div>Hello " . $user_input . "</div>";

// Command injection vulnerability
$command = "ping " . $_POST['host'];
system($command);

// Path traversal vulnerability
$file = $_GET['file'];
include($file);
?>
