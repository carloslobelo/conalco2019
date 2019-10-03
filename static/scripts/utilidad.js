function selectEnCombo(texto, idCombo){
    
    combo=document.getElementById(idCombo);
    for(i=1;i<combo.length; i++){
        if(combo.options[i].value==texto){
            combo.selectedIndex=i;
            break;
        }
    }
}
