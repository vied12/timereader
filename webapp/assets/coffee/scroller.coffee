class Scroller

  constructor: (content) ->
    @CONFIG =
      marginBottom      : 10        
      content           : content
      ratio             : 1
      currentArticle    : 0
      lastArticle       : 0

    @uis =
      articlesRead       :  $('.reader article')
      container           : $('.scroller')
      wrapper             : $('.wrapper')
      scroller            : $('.content')
      articles            : $('.scroller article') 
      lift                : $('.lift')
      topElement          : $('.bg-primary')

    @reader = $('.reader')
    this.init()
    this.relayout()
    $(window).resize this.relayout
    $(window).scroll this.scroll    
    
  init : =>
    @uis.scroller.html(@CONFIG.content)
    this.scroll() 
    ###    
    @uis.lift.draggable({ 
      axis: "y" , 
      containment: "parent" ,
      scroll: true,
      drag : (e, ui) =>
        stop = ui.offset.top / $(window).height() * $(document).height() 
        this.scrollTo(stop)
    })###

  relayout: (e) =>
    # when the header is displayed : height = $(window).height() - @uis.topElement.height() - @CONFIG.marginBottom
    height = $(window).height()  - @CONFIG.marginBottom
    @uis.container.height(height)
    @CONFIG.ratio = $(document).height() / @uis.scroller.height()  
    @uis.lift.height(height / @CONFIG.ratio)

  scroll:(e) =>
    this.scrollTo()
  
  scrollTo: (top) =>
    if top?
      stop = top
      console.log "stop", stop , "window", $(document).scrollTop() 
      $(window).scrollTop(stop)
    else
      stop = $(window).scrollTop()
      # when the header is displayed : stop = $(window).scrollTop() - @uis.topElement.height()

      # lift
      liftCentering  = $(window).height() * stop / $(document).height() 
      #lift position : begin at begin, move at center in the middle, finish at the end
      liftCentering = liftCentering - @uis.lift.height() * stop / $(document).height() 
      liftStop = 0 + liftCentering
      @uis.lift.css('top', liftStop+'px')

    # currentArticle  
    currentArticle = this.getCurrentArticle(stop)
    #console.log(">", currentArticle)
    scrollerArticles = @uis.scroller.find('article')
    scrollerArticle = $(scrollerArticles[currentArticle])
    scrollerArticles.each (i, el) => 
      $(el).removeClass('active')
    scrollerArticle.addClass('active')

    # scroller
    readerArticle =  $(@uis.articlesRead[currentArticle])
    currentArticleProgress = (stop-readerArticle.offset().top) * scrollerArticle.height() / readerArticle.height()
    scrollerTop = scrollerArticle.position().top + currentArticleProgress - liftCentering - (@uis.lift.height()/2 * stop / $(document).height())
    #  (@uis.lift.height() /2 * stop / $(document).height()) : adapt scrolltop to change article when cross middle of lift
    @uis.scroller.css('top', -scrollerTop+'px')

    # when the header is displayed :code to fix scroller 
    if(stop > @uis.topElement.height() or true) 
      @uis.container.css('position', 'fixed')
      @uis.container.height($(window).height() - @CONFIG.marginBottom)
    else
      @uis.container.css('position', 'absolute')
      this.relayout()
    



  getCurrentArticle: (position) =>
    currrent = @CONFIG.lastArticle
    @uis.articlesRead.each (i, el) =>
      article = $(el)
      if position > article.position().top and  position < (article.position().top + article.height() - @uis.lift.height()/2)
          currrent=i
          @CONFIG.lastArticle = i
          return false
    return currrent


class Reader

  constructor: (container)->

    @uis =
      container : $(container)
      articles : $(".reader article")
    #@uis.articles.find('*').removeAttr('style')
    @uis.articles.find('*').each (i, el) =>
      $(el).css('fontSize','')
    
        
    
    @scroller = new Scroller( @uis.articles.clone())
    $('.bg-secondary').hide()
    $('.bg-primary').hide()
    $('footer').hide()



reader = new Reader('.reader')