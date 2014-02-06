class Scroller

  constructor: (content) ->
    @CONFIG =
      marginBottom      : 10        
      content           : content

    @uis =
      reader              : $('.reader') 
      container           : $('.scroller')
      scroller            : $('.scroller-inner')
      articles            : $('.articles') 
      lift                : $('.lift')
      topElement          : $('.bg-primary')

    this.init()
    this.relayout()
    $(window).resize (e) -> this.relayout()
    $(window).scroll this.scroll    
    
  init : ->
    @uis.scroller.html(@CONFIG.content)

  relayout: ->
    height = $(window).height() - @uis.topElement.height() - @CONFIG.marginBottom
    #console.log height, @uis.topElement.height()
    @uis.container.height(height)

  scroll: (e) =>
    stop = $(window).scrollTop() - @uis.topElement.height()
    ratio = $(document).height() / @uis.scroller.height()  
    #console.log "stop", stop, "ratio", ratio
    @uis.scroller.css('top', (-stop/ratio)+'px')
    if(stop > @uis.topElement.height()) 
      @uis.container.css('position', 'fixed')
      @uis.container.height($(window).height() - @CONFIG.marginBottom)
    else
      @uis.container.css('position', 'absolute')
      this.relayout()   



class Reader

  constructor: (container)->
    @uis =
      container : $(container)
      articlesPositions : []
      articles : $(".articles")
    @scroller = new Scroller(@uis.articles.clone())
    this.articlesPositions()

  articlesPositions: =>
    @uis.articles.each (i,el) =>
      article = $(el)
      @CONFIG.articlesPositions.push article.offset().top
    console.log "@CONFIG.articlesPositions", @CONFIG.articlesPositions

reader = new Reader(".reader")
