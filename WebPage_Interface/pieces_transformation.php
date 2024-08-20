<html>

<head>

	<link href='https://fonts.googleapis.com/css?family=Muli' rel='stylesheet'>	
	<link rel="stylesheet" href="external_css.css">		
	<title>INFI - Pieces to Process</title> 
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
  <div><a href="pieces_deliver.php">Pieces to Deliver</a></div>
  <div><a href="pieces_produced.php">Processed Pieces</a></div>
  <div><a href="dock.php">Dock</a></div>
</div>

<h2 style="text-align:center;color:#b53f42;">Pieces to Process</h2>

   <table class ="center">

      <thead>
		 <th>Total Order ID</th>
		 <th>Individual Order ID</th>
         <th>Piece ID</th>
         <th>Initial Type</th>
         <th>Final Type</th>
		 <th>Machine</th>
		 <th>State</th>
      </thead>

      <tbody>

        <?php 
	    $pieces = "SELECT * FROM infi.mes_transformation_order";
	    $result = pg_exec($conn, $pieces);

        if(pg_num_rows($result) > 0)
        {
            while($row = pg_fetch_assoc($result))
            {
					?>
					<tr>	
						<td><?php echo $row['erp_id']?></td>
                        <td><?php echo $row['order_id']?></td>
						<td><?php echo $row['piece_id']?></td>
						<td><?php echo $row['initial_type']?></td>
						<td><?php echo $row['final_type']?></td>
                        <td><?php echo $row['machine']?></td>
						<td><?php echo $row['status']?></td>
					</tr>
					<?php
			}
                
        };
         ?>
      </tbody>

   </table>

   <br>

</body>