<?php 

    $connection = new PDO('mysql:host=localhost;dbname=test', 'root', '');
    $sql = 'SELECT * FROM HEMS_values';

    $data = $connection->query($sql);

    $rows = $data->fetchAll(PDO::FETCH_NUM);

    $counter=1;

    foreach($rows as $row) {
        

        ${'ID'.$counter}=$row[0];
        ${'Variablename'.$counter}=$row[1];
        ${'Variablevalue'.$counter}=$row[2];

        $counter++;

    }

    $hems_verbindung1 = $Variablevalue1;
    $hems_verbindung2 = $Variablevalue2;
    $openwb_connection_state = $Variablevalue3;
    $webasto_connection_state = $Variablevalue4;
    $openwb_charge_priority = $Variablevalue5;
    $webasto_charge_priority = $Variablevalue6;
    $openwb_charging_power = $Variablevalue7;
    $webasto_charging_power = $Variablevalue8;
    $pv_energy_share_webasto = $Variablevalue9;
    $pv_energy_share_openwb = $Variablevalue10;
    $remaining_time_webasto = $Variablevalue11;
    $remaining_time_openwb = $Variablevalue12;
    $demand_energy_openwb = $Variablevalue13;
    $demand_energy_webasto = $Variablevalue14;
    $charging_state_openwb = $Variablevalue15;
    $charging_state_webasto = $Variablevalue16;

    $Strompreis_aktuell = $Variablevalue17;
    $Stromnetzverwendung_aktuell = $Variablevalue18;
    $StromnetzverwendungLaden_aktuell = $Variablevalue19;
    $Ladekosten_aktuell = $Variablevalue20;
    $Gewinn_HEMS = $Variablevalue21;
    $Gewinn_HEMS_gesamt = $Variablevalue22;

    $ErzeugungPV_Energie = $Variablevalue23;
    $Haushalt_Stromverbrauch = $Variablevalue24;
    $Heimspeicher_Leistung = $Variablevalue25;
    $Heimspeicher_Ladezustand = $Variablevalue26;

    echo "hems_verbindung1 " . $hems_verbindung1 . "<br>";
    echo "hems_verbindung2 " . $hems_verbindung2 . "<br>";
    echo "openwb_connection_state " . $openwb_connection_state . "<br>";
    echo "webasto_connection_state " . $webasto_connection_state . "<br>";
    echo "openwb_charge_priority   " . $openwb_charge_priority   . "<br>";
    echo "webasto_charge_priority " . $webasto_charge_priority . "<br>";
    echo "openwb_charging_power " . $openwb_charging_power . "<br>";
    echo "webasto_charging_power " . $webasto_charging_power . "<br>";
    echo "pv_energy_share_webasto " . $pv_energy_share_webasto . "<br>";
    echo "pv_energy_share_openwb  " . $pv_energy_share_openwb  . "<br>";
    echo "remaining_time_webasto  " . $remaining_time_webasto  . "<br>";
    echo "remaining_time_openwb  " . $remaining_time_openwb  . "<br>";
    echo "demand_energy_openwb " . $demand_energy_openwb . "<br>";
    echo "demand_energy_webasto " . $demand_energy_webasto . "<br>";
    echo "charging_state_openwb " . $charging_state_openwb . "<br>";
    echo "charging_state_webasto " . $charging_state_webasto . "<br><br>";
    echo "Strompreis_aktuell " . $Strompreis_aktuell . "<br>";
    echo "Stromnetzverwendung_aktuell " . $Stromnetzverwendung_aktuell . "<br>";
    echo "StromnetzverwendungLaden_aktuell " . $StromnetzverwendungLaden_aktuell . "<br>";
    echo "Ladekosten_aktuell " . $Ladekosten_aktuell . "<br>";
    echo "Gewinn_HEMS " . $Gewinn_HEMS . "<br>";
    echo "Gewinn_HEMS_gesamt " . $Gewinn_HEMS_gesamt . "<br><br>";
    echo "ErzeugungPV_Energie " . $ErzeugungPV_Energie . "<br>";
    echo "Haushalt_Stromverbrauch " . $Haushalt_Stromverbrauch . "<br>";
    echo "Heimspeicher_Leistung " . $Heimspeicher_Leistung . "<br>";
    echo "Heimspeicher_Ladezustand " . $Heimspeicher_Ladezustand . "<br><br>";

    
?>

<?php 
if($_SERVER['REQUEST_METHOD'] === 'POST'){
    $connection = new PDO('mysql:host=localhost;dbname=test', 'root', '');
    $maxchargetime = $_POST['email']; 
    $sql = "INSERT INTO HEMS_values VALUES('100', 'Nutzerwahl_EndeLadung', '$maxchargetime', 'hh:mm') ON DUPLICATE KEY UPDATE VARIABLEVALUE = '$maxchargetime' ";
    $data = $connection->query($sql);
}

echo<<<_HTMLCODE
<form method="POST" action="display2.php" > 
<label>Minuten bis zur Volladung:</label> <input name="email" type="text"/>
<input type="submit" name="submit" value="Insert" /> <br>
</form> 
_HTMLCODE;

?>

