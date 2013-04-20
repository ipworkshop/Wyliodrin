$("#form-rem").submit(function(event) {

  event.preventDefault();

  var $form = $( this ),

      id = $form.find( 'input[name="id"]' ).val(),
	  email = $form.find( 'input[name="email"]' ).val(),

      url = $form.attr( 'action' );

 

  /* Send the data using post */

  var posting = $.post( url, { id: id, email: email} );

 

  /* Put the results in a div */

  posting.done(function( data ) {
  
    info = jQuery.parseJSON (data);
	if (info.result==1)
	{
		alert ("Your raspberry has been removed");
	}
	else
	{
		alert ("Invalid raspberry");
	}
  });

});


 

