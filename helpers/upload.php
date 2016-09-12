<?php

function generateRandomString($length = 8) {
   $characters = '0123456789abcdefghijklmnopqrstuvwxyz';
   $charactersLength = strlen($characters);
   $randomString = '';
   for ($i = 0; $i < $length; $i++) {
       $randomString .= $characters[rand(0, $charactersLength - 1)];
   }
   return $randomString;
}

$ip = $_SERVER['REMOTE_ADDR'];

if (!empty($_SERVER['HTTP_CLIENT_IP'])) {
   $ip .= "-".$_SERVER['HTTP_CLIENT_IP'];
}
if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
   $ip .= "-".$_SERVER['HTTP_X_FORWARDED_FOR'];
}

$agent = "dummy";
if(!empty($_GET['agent'])){
  $agent = $_GET['agent'];
}
if(!empty($_POST['agent'])){
  $agent = $_GET['agent'];
}

$target_dir = "/var/www/chat/".$ip."/".$agent."/";
if(!is_dir($target_dir)){
 if (!mkdir($target_dir, 0755, true)) {
   die('Failed to create directory: '.$target_dir);
 }
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
  $filename = "dummy";
  if (!empty($_FILES['file']) ){
    $filename = iconv("UTF-16","ISO-8859-1//TRANSLIT",base64_decode($_FILES['file']['name']));
    $target_file = $target_dir . $filename;
    if (file_exists($target_file)) {
       $target_file .= "." .generateRandomString();
    }
    if (move_uploaded_file($_FILES["file"]["tmp_name"], $target_file)) {
       echo "The file ". basename( $_FILES["file"]["name"]). " has been uploaded.";
    } else {
     echo "Sorry, there was an error uploading your file: cant move";
    }
  } else {
    echo "Sorry, there was an error uploading your file: no file";
  }
}
print_r($GLOBALS);
