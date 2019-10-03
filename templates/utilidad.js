function selectEnCombo(texto, idCombo){
    pos=-1;
    combo=document.getElementById(idCombo);
    for(i=0;i<combo.length; i++){
        if(combo.options[i].value==texto){
            pos=i;
            break;
        }
    }
    combo.selectedIndex=pos;
    alert("listo");
}