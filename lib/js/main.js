/************/
/* main.js */
/**********/

////////
//VAR
var selectedInput=0;
var currentTrip;
var hCercle = 10;
var urlApi = "http://10.5.0.124:5000";

var tmp = [{
    "thematic": "life-style", 
    "title": "A Perpignan, l'Afrique prend la parole", 
    "summary": "Filda Adoch, Ougandaise, commente les images de Martina Bacigalupo et sort des clich\u00e9s.", 
    "content": "Filda Adoch, Ougandaise, commente les images de Martina Bacigalupo et sort des clich\u00e9s.", 
    "source": "http://www.lemonde.fr/rss/tag/ete.xml", 
    "link": "", 
    "_id": {
        "$oid": "51a077eb3062721886fafe33"
    }
}, {
    "thematic": "life-style", 
    "title": "Li Chengpeng, le sport sans tabou en Chine", 
    "summary": "Ancien commentateur sportif, Li Chengpeng a choisi de se consacrer \u00e0 l'\u00e9criture apr\u00e8s avoir re\u00e7u des menaces de mort. Par le biais de son blog, mais aussi de fictions, il aborde sans fard les sujets qui d\u00e9rangent.", 
    "content": "Ancien commentateur sportif, Li Chengpeng a choisi de se consacrer \u00e0 l'\u00e9criture apr\u00e8s avoir re\u00e7u des menaces de mort. Par le biais de son blog, mais aussi de fictions, il aborde sans fard les sujets qui d\u00e9rangent.", 
    "source": "http://www.lemonde.fr/rss/tag/ete.xml", 
    "link": "", 
    "_id": {
        "$oid": "51a077eb3062721886fafe34"
    }
}, {
    "thematic": "life-style", 
    "title": "Christian Portal, soigner par les plantes", 
    "summary": "D\u00e9non\u00e7ant une d\u00e9marche de soin\u00a0\"tourn\u00e9e essentiellement sur l'augmentation des profits\", Christian Portal plaide, \u00e0 travers son blog, pour une m\u00e9decine \u00e9cologique.", 
    "content": "D\u00e9non\u00e7ant une d\u00e9marche de soin\u00a0\"tourn\u00e9e essentiellement sur l'augmentation des profits\", Christian Portal plaide, \u00e0 travers son blog, pour une m\u00e9decine \u00e9cologique.", 
    "source": "http://www.lemonde.fr/rss/tag/ete.xml", 
    "link": "", 
    "_id": {
        "$oid": "51a077eb3062721886fafe35"
    }
}, {
    "thematic": "life-style", 
    "title": "Anne Lataillade, du beau et du bon au menu", 
    "summary": "Fuyant les plats compliqu\u00e9s, Anne Lataillade propose, via son blog, \"Papilles et pupilles\", des recettes inspir\u00e9es par une cuisine familiale, \u00e0 la port\u00e9e de tous.", 
    "content": "Fuyant les plats compliqu\u00e9s, Anne Lataillade propose, via son blog, \"Papilles et pupilles\", des recettes inspir\u00e9es par une cuisine familiale, \u00e0 la port\u00e9e de tous.", 
    "source": "http://www.lemonde.fr/rss/tag/ete.xml", 
    "link": "", 
    "_id": {
        "$oid": "51a077eb3062721886fafe36"
    }
}, {
    "thematic": "life-style", 
    "title": "\"La prestesse du mal est inou\u00efe\"", 
    "summary": "", 
    "content": "", 
    "source": "http://www.lemonde.fr/rss/tag/ete.xml", 
    "link": "", 
    "_id": {
        "$oid": "51a077eb3062721886fafe37"
    }
}];

//////////////
// FUNCTIONS
function updateDim(){
    $("body div#home").height($(window).height());
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
            
            //templating
            //var data = tmp;
            //var html = template_results({results:data});
            var html = template_results({
                results:data.articles
                });
            $("div#results ul").html(html);    
            html = template_detailsresults(currentTrip);
            $("div#results div#detailsResults").html(html);    

            //affichage
            goToPage("results");

            $("div#results ul li").click(function(e){
                var selectedArticle = data.articles[$(e.currentTarget).data("id")];
                //charger le contenu
                load_content(selectedArticle);
                //aller à la page
                goToPage("reader");
            });            
        }
    });    
   
}

function load_content(article){
    //console.log($("div#reader div#content").height());
    
    /*$("div#reader div#content").ready(function(){
        //console.log($("div#container").height());
        drawLignes(currentTrip);
    });*/
    var oid = article._id.$oid;
    console.log(oid);
    $.ajax({
        url: urlApi+"/api/content/"+oid,
        type: 'get',
        /*dataType: 'json',*/
        success: function (data) {
            $("div#reader div#content").html(data);
            $("div#reader div#content").ready(function(){
                //console.log($("div#container").height());
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
    var contentHeight = $("div#container").height();    
    $("div#visu").height(contentHeight);
    $("div#ligne").height(contentHeight);
    var interStation = (contentHeight - (nbStations * hCercle)) / nbStations;
    
    var html = template_cerclestation({
        couleur: "#786534"
    });
    for(var i = 0; i< nbStations; i++){        
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
   
   
    //
    updateDim();
   
    //events
    $(window).resize(function(){
        updateDim();
    })
});