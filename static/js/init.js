(function($){
  $(function(){

    $('.sidenav').sidenav();
    $('.parallax').parallax();

  }); // end of document ready
})(jQuery); // end of jQuery name space

function lireAnnotation() {
  var annotation = document.getElementById("annotation").innerText;
  // utilisation de la  bibliothèque de synthèse vocale pour lire l'annotation
  var synth = window.speechSynthesis;
  var utterance = new SpeechSynthesisUtterance(annotation);
  synth.speak(utterance);

}



