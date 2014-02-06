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
    
  init : ->
    @uis.scroller.html(@CONFIG.content)
    this.scroll() 

  relayout: (e) =>
    # when the header is displayed : height = $(window).height() - @uis.topElement.height() - @CONFIG.marginBottom
    height = $(window).height()  - @CONFIG.marginBottom
    @uis.container.height(height)
    @CONFIG.ratio = $(document).height() / @uis.scroller.height()  
    @uis.lift.height(height / @CONFIG.ratio)

  scroll: (e) =>
    # when the header is displayed : stop = $(window).scrollTop() - @uis.topElement.height()
    stop = $(window).scrollTop()
    stopDoc = $(document).scrollTop()

    # currentArticle  
    currentArticle = this.getCurrentArticle(stop)
    #console.log(">", currentArticle)
    scrollerArticles = @uis.scroller.find('article')
    scrollerArticle = $(scrollerArticles[currentArticle])
    scrollerArticles.each (i, el) => 
      $(el).removeClass('active')
    scrollerArticle.addClass('active')

    # lift
    liftCentering  = $(window).height() * stop / $(document).height() 
    #lift position : begin at begin, move at center in the middle, finish at the end
    liftCentering = liftCentering - @uis.lift.height() * stop / $(document).height() 
    liftStop = 0 + liftCentering
    @uis.lift.css('top', liftStop+'px')

    # scroller
    readerArticle =  $(@uis.articlesRead[currentArticle])
    currentArticleProgress = (stop-readerArticle.offset().top) * scrollerArticle.height() / readerArticle.height()
    scrollerTop = scrollerArticle.position().top+currentArticleProgress-liftCentering
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
      if position > article.offset().top and  position < (article.offset().top + article.height())
          currrent=i
          @CONFIG.lastArticle = i
          return false
    return currrent


class Reader

  constructor: (container)->

    @uis =
      container : $(container)
      articles : $(".reader article")
    @scroller = new Scroller( @uis.articles.clone())
    $('.bg-secondary').hide()
    $('.bg-primary').hide()
    $('footer').hide()

reader = new Reader('.reader')