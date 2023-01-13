$(function(){
function Open(){
	$('#Dimas').toggleClass('BatyaOn');
	$('#Dimas').removeClass('BatyaOff');
}
function OffLead(){
	$('#OffLeadOf').toggleClass('Off');
	$('#OffleadOf').removeClass('On');
}
function off(){
    $('#Dimas').toggleClass('BatyaOff');	
    $('#OffLeadOf').toggleClass('On');	
}	
$('#TurnOn').on('click', function(){		
	Open();	
	OffLead()
});		
$('#TurnOff').on('click', function(){		
	off();	
	setTimeout(Open, 0);			
});	
});
