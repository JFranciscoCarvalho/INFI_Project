<html>

<head>

	<link href='https://fonts.googleapis.com/css?family=Muli' rel='stylesheet'>	
	<link rel="stylesheet" href="external_css.css">		
	<title>INFI - Processed Pieces</title> 
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

<?php 
$conn = pg_connect("host=db.fe.up.pt dbname=pswa0502 user=pswa0502 password=jKWlEeAs");	
pg_exec($conn, $query);
?>

<h1 style="text-align:center;color:#b53f42;margin-top:50px;">INFI Project</h1>

<div class="container space-around">
  <div><a href="home.php">Home</a></div>
  <div><a href="Machines.php">Machines</a></div>
  <div><a href="pieces_transformation.php">Pieces to be Processed</a></div>
  <div><a href="pieces_deliver.php">Pieces to Deliver</a></div>
  <div><a href="dock.php">Dock</a></div>
</div>

<h2 style="text-align:center;color:#b53f42;">Processed Pieces</h2>

   <table class ="center">

      <thead>
         <th>Piece ID</th>
         <th>Piece Type</th>
         <th>Arrival Day</th>
		 <th>Cost</th>
		 <th>Production Time</th>
      </thead>

      <tbody>

        <?php 
	    $pieces = "SELECT * FROM infi.pieces";
	    $result = pg_exec($conn, $pieces);

        if(pg_num_rows($result) > 0)
        {
            while($row = pg_fetch_assoc($result))
            {
					?>
					<tr>	
						<td><?php echo $row['id']?></td>
                        <td><?php echo $row['piece_type']?></td>
						<td><?php echo $row['arrival_day']?></td>
						<td><?php echo $row['cost']?></td>
                        <td><?php echo $row['production_time']?></td>
					</tr>
					<?php
			}
                
        };
         ?>
      </tbody>

   </table>

   <br>

</body>