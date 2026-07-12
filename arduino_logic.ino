// Arduino UNO Q logic (merge with your existing sensor code)

void applyStatus(String status){
  if(status=="NORMAL"){
    safeMode();
  }else if(status=="WARNING"){
    warningMode();
  }else if(status=="ALERT"){
    dangerMode();
  }
}

void checkIncomingCommand(){
  if(Serial.available()){
    String cmd=Serial.readStringUntil('\n');
    cmd.trim();
    applyStatus(cmd);
  }
}

// In loop(), after printing sensor values:
// checkIncomingCommand();
