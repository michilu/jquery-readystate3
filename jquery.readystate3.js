(function($){
 $.readyState3 = {
  VERSION: '0.1',
  options: {
   HOST: 'undefined',
   PORT: 'undefined',
   PATH: "\/",
   CALLBACK: function( data ){ eval(data); }
  },
  option: function( name, value ){
   $.readyState3.options[name] = value;
  },
  url: function(){
   var _ = $.readyState3.options;
   var base = ""; var HOST = _["HOST"];
   if ( HOST != 'undefined' ) {
    base = 'http:\/\/' + HOST;
    var POST = _["PORT"];
    if ( PORT != 'undefined' )
     base = base + ":" + PORT;
   };
   return base + _["PATH"] + '#' + (new Date()).getTime()
  },
  connect: function(){
   var $readyState3 = $.readyState3;
   var $state = $readyState3.state;
   var $con = $state.connection;
   if ( $con != 'undefined' )
    $readyState3.disconnect();
   var $con = new XMLHttpRequest();
   $con.onreadystatechange = function(){
    if ( this.readyState == 3 ){
     var $response = this.responseText;
     var length = $response.length;
     var data;
     try {
      data = $response.slice($state.POS);
     } catch(e){};
     $state.POS = length;
     $readyState3.options.CALLBACK(data);
    };
   };
   $con.open("GET", $.readyState3.url(), true);
   $con.send(null);
   $readyState3.state.connection = $con;
  },
  disconnect: function(){
   var $state = $.readyState3.state;
   var $con = $state.connection;
   $con.abort();
   $state.reset();
  },
  state: {
   connection: 'undefined',
   POS: 0,
   reset: function(){
    $state = $.readyState3.state;
    $state.connection = 'undefined';
    $state.POS = 0;
   }
  }
 };
})(jQuery);

