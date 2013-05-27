/************/
/* main.js */
/**********/

////////
//VAR
var selectedInput=0;
var currentTrip;
var hCercle = 20;
var urlApi = "";
var currentCounter = 0;
var totalCounter = 0;

//////////////
// FUNCTIONS
function updateDim(){
    $("body div#home").height($(window).height());
	$("body div#homeTmp").height($(window).height());
//$("body div#container").width($(window).width());
}

function goToPage(id){
    $("body div.page").hide();
    $("body div#"+id).fadeIn();
}

function startSearch(){
    //traitement
    //requete
    var scoord = $("input#startcoord").val();
    var ecoord = $("input#endcoord").val();

    if(! scoord || !ecoord){
        $("div#searchAlert").removeClass("hidden").addClass("alert");
        return 0;            
    }
    
    $.ajax({
        url: urlApi+"/api/itineraire/"+scoord+"/"+ecoord,
        type: 'get',
        dataType: 'json',
        success: function (data) {
            currentTrip=data;
            currentTrip["nbStations"]=currentTrip.stations.length;
            currentTrip["duree"]=currentTrip.delta / 60;
            //details
            html = template_detailsresults(currentTrip);
            $("div#results div#detailsResults").html(html);
            
            //templating des resultats
            var html1 = template_results({
                results:data.articles.one
            });
            $("div#results ul").html(html1);
            $("div#results ul").append(template_audio({}));
            
            //affichage
            goToPage("results");

            $("div#results ul li").click(function(e){
                var selectedArticle = data.articles.one[$(e.currentTarget).data("id")];
                //charger le contenu
                load_content(selectedArticle);
                //aller à la page
                goToPage("reader");
            });            
        }
    });    
   
}

function load_content(article){
    var oid = article._id.$oid;
    console.log(oid);
    $.ajax({
        url: urlApi+"/api/content/"+oid,
        type: 'get',
        /*dataType: 'json',*/
        success: function (data) {
            $("div#reader div#content").html(data);
            var bottom = 
            '<br /><br /><a class="btn btn-primary btn-large"><i class="icon-plus-sign icon-white"></i>&nbsp;Plus de contenu</a>'+
            '&nbsp;&nbsp;&nbsp;<a class="btn btn-primary btn-large"><i class="icon-share icon-white"></i>&nbsp;Partager sur ma ligne</a>'
            $("div#reader div#content").append(bottom);
            $("div#reader div#content").ready(function(){
                drawLignes(currentTrip);
            });
        }    
    });
    
//fake
//$("div#reader div#content").height("1000px");
    
//drawLignes
    
}

function drawLignes(trip){
    //console.log(trip);
    //recup nb de stations puis la heuteur de la div
    var nbStations = trip.stations.length;
    var contentHeight = $(window).height();    
    $("div#visu").height(contentHeight);
    $("div#ligne").height(contentHeight);
    var interStation = (contentHeight - (nbStations * hCercle)) / nbStations;
    
    totalCounter = nbStations;
    for(var i = 0; i< nbStations; i++){        
        var html = template_cerclestation({
            couleur: "b40000",
            id: i
        });        
        $("div#visu ul").append(html);
    }
    
    $("div#visu ul li").css("margin-top",interStation+"px");
    $("div#visu ul li:first").css("margin-top",0);
//tracé les infos
}

//////////
// INIT
$(document).ready(function(){
    //init
    
    //templates
    template_results = Handlebars.compile($("#template-results").html());
    template_detailsresults = Handlebars.compile($("#template-detailsresults").html());
    template_cerclestation = Handlebars.compile($("#template-cerclestation").html());
    template_audio = Handlebars.compile($("#template-audio").html());
    
    //TYPEAHEAD
    $('input#start, input#end').typeahead({
        minLength: 2,
        source: function (query, process) {
            stations = [];
            map = {};
 
            $.ajax({
                url: urlApi+"/api/stations/autocomplete/"+query,
                type: 'get',
                dataType: 'json',
                success: function (data) {
                    $.each(data, function (i, station) {
                        map[station.name] = station;
                        stations.push(station.name);
                    });
                    process(stations);
                }
            });
 
        },
        matcher: function (item) {
            if (item.toLowerCase().indexOf(this.query.trim().toLowerCase()) != -1) {
                return true;
            }
        },
        sorter: function (items) {
            return items.sort();
        },
        updater: function (item) {
            selected = map[item].uri;
            if(selectedInput === 1)
                $("input#startcoord").val(selected);
            else
                $("input#endcoord").val(selected);
            return item;        
        }            
    });
   
   
    $('#sl1').slider({
        formater: function(value) {
            return value*10 + "min";
        }
    });
   
    //
    updateDim();
   
    //events
    $(window).resize(function(){
        updateDim();
    })
    
    $(window).scroll(function(){
        console.log($(document).height() + " " + ($(window).scrollTop()+$(window).height()));
        var section = $(document).height() / totalCounter;
        if($(window).scrollTop() > section * currentCounter){
            $("#circle-"+currentCounter).attr("fill","#b40000");
            currentCounter++;
        }
    });
});