<html>

<head>

	<link href='https://fonts.googleapis.com/css?family=Muli' rel='stylesheet'>	
	<link rel="stylesheet" href="external_css.css">		
	<title>INFI - Machines</title> 
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
  <div><a href="pieces_transformation.php">Pieces to be Processed</a></div>
  <div><a href="pieces_deliver.php">Pieces to Deliver</a></div>
  <div><a href="pieces_produced.php">Processed Pieces</a></div>
  <div><a href="dock.php">Dock</a></div>
</div>

<h2 style="text-align:center;color:#b53f42;">Machines Performance</h2>

   <table class ="center">

      <thead>
         <th>Machine</th>
         <th>Total Operating Time</th>
         <th>Total Operated Pieces</th>
		 <th>P1</th>
		 <th>P2</th>
		 <th>P3</th>
		 <th>P4</th>
		 <th>P5</th>
		 <th>P6</th>
		 <th>P7</th>
		 <th>P8</th>
		 <th>P9</th>
      </thead>

      <tbody>

        <?php 
	    $machine = "SELECT * FROM infi.machine";
	    $result = pg_exec($conn, $machine);

        if(pg_num_rows($result) > 0)
        {
            while($row = pg_fetch_assoc($result))
            {
					?>
					<tr>	
						<td><?php echo $row['name']?></td>
                        <td><?php echo $row['total_operating_time']?></td>
						<td><?php echo $row['total_operated_pieces']?></td>
						<td><?php echo $row['p1']?></td>
                        <td><?php echo $row['p2']?></td>
						<td><?php echo $row['p3']?></td>
						<td><?php echo $row['p4']?></td>
                        <td><?php echo $row['p5']?></td>
						<td><?php echo $row['p6']?></td>
						<td><?php echo $row['p7']?></td>
                        <td><?php echo $row['p8']?></td>
						<td><?php echo $row['p9']?></td>
					</tr>
					<?php
			}
                
        };
         ?>
      </tbody>

   </table>

   <br>



</body>