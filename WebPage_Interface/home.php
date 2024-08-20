<html>

<head>

	<link href='https://fonts.googleapis.com/css?family=Muli' rel='stylesheet'>	
	<link rel="stylesheet" href="external_css.css">		
	<title>INFI - Home Page</title> 
	<meta charset="UTF-8">
	
</head>

	<style>
	.center 
	{
		margin-left: auto;
		margin-right: auto;
	}
    .position
   	{
      margin-top:100px;
	  position:center;
   	}
	table 
	{
		border-collapse: collapse; 
   	}
		
	table, th, td 
   	{
      border:1px solid;
	}
		
	th, td 	
   	{
      padding:10px 
	}

	.container 
	{
		width: 650px;
		margin: auto;
		display: flex;
	}
	.container.space-around 
	{
		justify-content: space-around;
	}
	
	</style>

<body>

<h1 style="text-align:center;color:#b53f42;margin-top:50px;">INFI Project</h1>

<p class="container" style="text-align: justify;"> In this page, you can find the user Interface for the INFI Project. The user will be able to see how many and what pieces are to be delivered, are to be transformed and are to be delivered. 
The User will also be able to see the Machine's performance and the how many and what pieces have been delivered in each dock. </p>
<br>
<p class="container" style="text-align: justify;"> Project developed by: Francisco Carvalho, Manuel Silva, Pedro Barros, Henrique and Sixto</p>
<br>
<p class="container" style="text-align: justify;"> In order to execute the program download the Instructions &nbsp; <a href="instructions.txt">here</a> </p>
<br>
<div class="container space-around" >
  <div><a href="Machines.php">Machines</a></div>
  <div><a href="pieces_transformation.php">Pieces to be Processed</a></div>
  <div><a href="pieces_deliver.php">Pieces to Deliver</a></div>
  <div><a href="pieces_produced.php">Processed Pieces</a></div>
  <div><a href="dock.php">Dock</a></div>
</div>


</body>