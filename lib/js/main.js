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
var valTimer = 1;

var stationFilled = "#DCDCDC";
var hasLS=1;

var tabThematics=[
	{name: "Les dossiers Streetpress", slug: "streetpress"},
	{name: "Design", slug: "design"},
	{name: "Technologie", slug: "technologie"},
	{name: "Nouveaux Médias", slug: "new-media"},
	{name: "Littérature", slug: "literature"},
	{name: "Musique", slug: "music"},
	{name: "Lifestyle", slug: "lifestyle"},
	{name: "Voyage", slug: "travel"},
	{name: "Ile-de-France",slug: "idf"}
];

var mode = "";

//////////////
// FUNCTIONS
function updateDim(){
    $("body div#home").height($(window).height());
	$("body div#homeTmp").height($(window).height());
	$("body div#main").height($(window).height());
	$("body div#settings").height($(window).height());
	
	//$("body div#container").width($(window).width());
}

function contentSize(factor){
	var div=$("div#reader div#content div#contentArticle");
	
	div.css("font-size",String(parseInt(div.css("font-size"))+factor)+"px");
	div.css("line-height",String(parseInt(div.css("line-height"))+factor)+"px");
}

function connectToReadability(){
	var login=$("input#readabUser").val();
	var pass=$("input#readabPass").val();
	
	$.ajax({
		url: urlApi+"/api/readability/"+login+"/"+pass,
		type: 'get',
		dataType: "json",
		success: function(data,status){
			if(hasLS){
				localStorage.setItem("tr-user-id",data.user);
				localStorage.setItem("tr-readability-ok","1");
				$("div#subReadability").html("Connexion à Readability OK");
			}
		},
		error: function(){
			$("div#subReadability").append("<br /><strong>Problème lors de la connexion</strong>");
		}
	});
}

function saveSettings(){
	var thematics="";
	
	$("div#intSettings input[type=checkbox]").each(function(item){
		if($(this)[0].checked)
			thematics+=$(this).val()+",";
		
		if(thematics!="")
			localStorage.setItem("tr-thematics",thematics.substring(0,thematics.length - 1));
		else
			localStorage.removeItem("tr-thematics");
	});

	goToPage("main");
}

function goToPage(id){
    $("body div.page").hide();
    $("body div#"+id).fadeIn();
	
	//cas spécifique
	if(id=="settings"){
		//loading des préférences
		if(localStorage.getItem("tr-readability-ok")!=null)
			$("div#subReadability").html("Connexion à Readability OK");
		
		//gen des checkbox		
		var thematics = localStorage.getItem("tr-thematics");
		if(thematics!=null){
			var pref=thematics.split(",");
			_.forEach(tabThematics,function(item){
				console.log(item);
				if(pref.indexOf(item.slug) > -1)
					item.checked="checked";
			});
		}
		var tmp = {
			results: tabThematics
		}
		var html = template_theme_checkbox(tmp);
		$("div#settings div#intSettings ul").html(html);		
	}
}


function startSearch(){
    //traitement
    //requete
    var scoord = $("input#startcoord").val();
    var ecoord = $("input#endcoord").val();	
	var urlSearch = "";
	
    if(! scoord || !ecoord){
        /*$("div#searchAlert").removeClass("hidden").addClass("alert");
        return 0;*/
		//MODE TEMPS
		urlSearch=urlApi+"/api/duration/"+(valTimer*60);
		mode = "temps";
    }else{
		//MODE ITINERAIRE
		urlSearch=urlApi+"/api/itineraire/"+scoord+"/"+ecoord;
		mode = "trajet";
	}

	//OPTIONS
	var thematics = localStorage.getItem("tr-thematics");
	if(thematics != null)	
		urlSearch +="/thematics/"+thematics;
	var userId = localStorage.getItem("tr-user-id");
	if(userId != null)	
		urlSearch +="/user/"+userId;			
    
    $.ajax({
        url: urlSearch,
        type: 'get',
        dataType: 'json',
        success: function (data) {
            currentTrip=data;
			
			//calcul du nb de station
			var nb = 0;
			var ns = 0;
			var textLignes = "";
			_.forEach(currentTrip.sections,function(s){
				nb += s.stations.length;
				ns++;
				textLignes+=s.line+", ";
			});
			
            currentTrip["nbStations"]=nb;			
			
			if(ns > 1){
				currentTrip["nbSections"]=ns - 1;
				currentTrip["lignes"]="Ligne "+textLignes.substring(0,textLignes.length - 2);
			}else{
				currentTrip["lignes"]="Lignes "+textLignes.substring(0,textLignes.length - 2);
			}
            
			//durée en minute
			currentTrip["duree"]= Math.round(currentTrip.delta / 60);
			
			//details
			if(mode == "trajet"){
				html = template_detailsresults(currentTrip);
			}else{
				html = template_detailsresults2(currentTrip);
			}		
            //html = template_detailsresults(currentTrip);
            $("div#results div#detailsResults").html(html);
            
            //templating des resultats
            var html1 = template_results({
                results:data.articles.one
            });
            $("div#results ul#listResults").html(html1);
			
			//TMP AUDIO
            //$("div#results ul#listResults").append(template_res_audio({}));//TMP à supprimer des démos tant que l'audio n'est pas activé
            
            //affichage
            goToPage("results");					

            $("div#results ul#listResults li").click(function(e){
				var selectedLi = $(e.currentTarget);
                var selectedArticle = data.articles.one[selectedLi.data("id")];
                //charger le contenu
				if(selectedLi.data("type") === "audio")
					load_audio(selectedArticle);
				else
					load_content(selectedArticle,currentTrip["duree"]);
                //aller à la page
                goToPage("reader");
            });            
        }
    });    
   
}

function load_content(article,duration){
    var oid = article._id.$oid;
	var d = new Date(article.date).toDateString();;

	var detailsContent = {
		title: article.title,
		date: d,
		source: article.domain.replace("www.",""),
		duree: duration
	}
	$("div#reader div#content").html(template_article(detailsContent));		
	
    $.ajax({
        url: urlApi+"/api/content/"+oid,
        type: 'get',
        /*dataType: 'json',*/
        success: function (data) {				
			$("div#reader div#content div#contentArticle").html(data);
			
			$("div#reader div#content div.metaArticle").css('background-image', 'none');
			$("div#reader div#content div.metaArticle").css('background-color', '#eb4e65');
			
            $("div#reader div#content div#contentArticle").ready(function(){
                drawLignes(currentTrip);
            });
        }    
    });       
}

function load_audio(article){
	var detailsAudio = {
		title: "test",
		content: "La chronique de Chris Esquerre",
		file: "http://media.radiofrance-podcast.net/podcast09/12879-30.05.2013-ITEMA_20485758-0.mp3"
	}
	$("div#reader div#content").html(template_audio(detailsAudio));
	$("div#reader div#content").ready(function(){
		$( 'audio' ).audioPlayer({
			classPrefix: 'audioplayer',
			strPlay: 'Play',
			strPause: 'Pause',
			strVolume: 'Volume'
		});
	});
}

function drawLignes(trip){
    //console.log(trip);
    //recup nb de stations puis la hauteur de la div
    var nbStations = trip.nbStations;
    var contentHeight = $(window).height();    
    $("div#visu").height(contentHeight);
    $("div#ligne").height(contentHeight);
    var interStation = (contentHeight - (nbStations * hCercle)) / nbStations;
    
    totalCounter = nbStations;
    for(var i = 0; i< nbStations; i++){        
        var html = template_cerclestation({
            couleur: "F0F0F0", //Note: a adapter avec la ligne...
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
	
	//Local Storage test
	if (Modernizr.localstorage) {
	  // window.localStorage is available!
	  localStorage.setItem("tr-version","0.1");
	} else {
	  // no native support for HTML5 storage :(
	  hasLS=0;
	}	
    
    //templates
    template_results = Handlebars.compile($("#template-results").html());
    template_detailsresults = Handlebars.compile($("#template-detailsresults").html());
	template_detailsresults2 = Handlebars.compile($("#template-detailsresults2").html());
    template_cerclestation = Handlebars.compile($("#template-cerclestation").html());
    template_res_audio = Handlebars.compile($("#template-res-audio").html());
	template_audio = Handlebars.compile($("#template-audio").html());
	template_article = Handlebars.compile($("#template-article").html());
	template_theme_checkbox = Handlebars.compile($("#template-theme-checkbox").html());
    
    //TYPEAHEAD
    $('input#start, input#end').typeahead({
        minLength: 2,
        source: _.debounce(function (query, process) {
            $.ajax({
                url: urlApi+"/api/stations/autocomplete/"+query,
                type: 'get',
                dataType: 'json',
                success: function (data) {
					stations = [];
					map = {};
                    $.each(data, function (i, station) {
                        map[station.name] = station;
                        stations.push(station.name);
                    });
                    process(stations);
                }
            });
        },500, true),
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
   
   
	//slider
	$("#timeSlider").simpleSlider({
		range: [1,120],
		highlight: true,
		step: 1
	});
	$("#timeSlider").bind("slider:changed", function (event, data) {
	  // The currently selected value of the slider
	  //console.log(data.value);
	  $("li#selected").html(data.value+"min");
	  valTimer = data.value;
	});   
    //
    updateDim();
   
   
	//handlers
	$("a[data-bghover]").hover(function(){
		$(this).data("tmp",$(this).css("background-image"));
		$(this).css("background-image","url('"+$(this).data("bghover")+"')");
	},function(){
		$(this).css("background-image",$(this).data("tmp"));
	});
	
	//click settings
	$("div#netSettings ul li a").click(function(){
		$("div.sub").slideUp();
		$(this).siblings("div.sub").slideDown();
	});
   
    //events
    $(window).resize(function(){
        updateDim();
    })
    
    $(window).scroll(function(){
        //console.log($(document).height() + " " + ($(window).scrollTop()+$(window).height()));
		var avance = $(window).scrollTop() * ($(window).height()) / ($(document).height()-$(window).height());
        var section = ($(document).height() - $(window).height()) / totalCounter;
		
		//console.log($(window).scrollTop()+" / "+$(document).height()+" / "+$(window).height());

		
		$("#avancement").height(avance);		
        if($(window).scrollTop() > section * currentCounter){
            $("#circle-"+currentCounter).attr("fill",stationFilled);			
            currentCounter++;
        }
    });
});