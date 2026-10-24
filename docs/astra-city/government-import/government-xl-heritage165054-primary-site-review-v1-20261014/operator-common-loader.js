

    
var ua = navigator.userAgent.toLowerCase(),
    isChrome = ua.indexOf("chrome") > -1,
    isSafari = /^((?!chrome|android).)*safari/i.test(ua),
    isFirefox = "undefined" != typeof InstallTrigger,
    isIE = detectIE(),
    isTouch = $(".touchevents").length;

function detectIE() {
    var e = window.navigator.userAgent,
        t = e.indexOf("MSIE ");
    if (t > 0) return parseInt(e.substring(t + 5, e.indexOf(".", t)), 10);
    if (e.indexOf("Trident/") > 0) {
        var n = e.indexOf("rv:");
        return parseInt(e.substring(n + 3, e.indexOf(".", n)), 10)
    }
    var i = e.indexOf("Edge/");
    return i > 0 && parseInt(e.substring(i + 5, e.indexOf(".", i)), 10)
}
var prefix = function () {
    var e = window.getComputedStyle(document.documentElement, ""),
        t = (Array.prototype.slice.call(e).join("").match(/-(moz|webkit|ms)-/) || "" === e.OLink && ["", "o"])[1];
    return {
        dom: "WebKit|Moz|MS|O".match(new RegExp("(" + t + ")", "i"))[1],
        lowercase: t,
        css: "-" + t + "-",
        js: t[0].toUpperCase() + t.substr(1)
    }
}();
isChrome && $("html").addClass("chrome"), isSafari && $("html").addClass("safari"), isFirefox && $("html").addClass("firefox"), isIE && $("html").addClass("ie ie-" + isIE);
var clickEvent = isTouch ? "touchend" : "click",
    resizeEvent = "orientationchange" in window ? "orientationchange" : "resize",
    animationEnd = function (e) {
        var t = {
            animation: "animationend",
            OAnimation: "oAnimationEnd",
            WebkitAnimation: "webkitAnimationEnd"
        };
        for (var n in t)
            if (void 0 !== e.style[n]) return t[n]
    }(document.createElement("div")),
    transitionEnd = function (e) {
        var t = {
            transition: "transitionend",
            OTransition: "oTransitionEnd",
            WebkitTransition: "webkitTransitionEnd"
        };
        for (var n in t)
            if (void 0 !== e.style[n]) return t[n]
    }(document.createElement("div")),
    $window = $(window),
    $html = $("html"),
    $body = $("body");

function getLang() {
    var e = $html.attr("lang");
    return "en" == e ? "en" : "zh-hk" == e ? "zh-hk" : "zh-cn" == e ? "zh-cn" : "en"
    // return "en" == e ? "en" : "tc" == e ? "zh-hk" : "sc" == e ? "zh-cn" : "en"
}

function langArg(e) {
    return e[getLang()]
}

function ckSTab(e) {
    return 9 == e.which && e.shiftKey
}

function ckTab(e) {
    return 9 == e.which && !e.shiftKey
}

function ckEsc(e) {
    return 27 == e.which && !e.shiftKey
}

function getUrlParams(e) {
    var t = e ? e.split("?")[1] : window.location.search.slice(1),
        n = decodeURIComponent(t),
        i = {};
    if (n)
        for (var o = (n = n.split("#")[0]).split("&"), r = 0; r < o.length; r++) {
            var s = o[r].split("="),
                a = s[0],
                l = void 0 === s[1] || s[1];
            if (a.match(/\[(\d+)?\]$/)) {
                var c = a.replace(/\[(\d+)?\]/, "");
                if (i[c] || (i[c] = []), a.match(/\[\d+\]$/)) {
                    var u = /\[(\d+)\]/.exec(a)[1];
                    i[c][u] = l
                } else i[c].push(l)
            } else i[a] ? i[a] && "string" == typeof i[a] ? (i[a] = [i[a]], i[a].push(l)) : i[a].push(l) : i[a] = l
        }
    return i
}

function isRetinaDisplay() {
    if (window.matchMedia) {
        var e = window.matchMedia("only screen and (min--moz-device-pixel-ratio: 1.3), only screen and (-o-min-device-pixel-ratio: 2.6/2), only screen and (-webkit-min-device-pixel-ratio: 1.3), only screen  and (min-device-pixel-ratio: 1.3), only screen and (min-resolution: 1.3dppx)");
        return e && e.matches || window.devicePixelRatio > 1
    }
}

function throttle(e, t) {
    var n = !0;
    return function (i) {
        n && (n = !1, setTimeout(function () {
            n = !0
        }, t), e(i))
    }
}

function looseParse(e) {
    return Function('"use strict";return (' + e + ")")()
}

jQuery.fn.outerHTML = function () {
    return jQuery("<div />").append(this.eq(0).clone()).html()
}, jQuery.fn.nextOrFirst = function (e) {
    var t = this.next(e);
    return t.length ? t : this.prevAll(e).last()
}, jQuery.fn.prevOrLast = function (e) {
    var t = this.prev(e);
    return t.length ? t : this.nextAll(e).last()
}, jQuery.fn.reverse = [].reverse, jQuery.fn.shuffle = function () {
    for (var e, t = 0; t < this.length; t++) e = Math.floor(Math.random() * this.length), $(this[t]).before($(this[e]));
    return this
};

function checkURLexist(e) {
    return e = e.replace("#top", ""), window.XMLHttpRequest ? (xhttp = new XMLHttpRequest, xhttp.open("GET", e, !1), xhttp.send(null), 200 == xhttp.status) : (xhttp = new ActiveXObject("Microsoft.XMLHTTP"), xhttp.open("GET", e, !1), xhttp.send(null), 200 == xhttp.status)
}

function validateSwapLangURL(text) {
	var tmpText = text.replace(/"/g, "′");
	tmpText = tmpText.replace(/'/g, "′");
	return tmpText;
}

function swapLang(e) {
    var t = String(window.location.href),
        n = "";
    if (-1 != t.indexOf("/tc/") && (n = "zh-hk"), -1 != t.indexOf("/en/") && (n = "en"), -1 != t.indexOf("/sc/") && (n = "zh-cn"), "en" == e ? "zh-hk" == n ? t = t.replace("/tc/", "/en/") : "zh-cn" == n && (t = t.replace("/sc/", "/en/")) : "zh-hk" == e ? "en" == n ? t = t.replace("/en/", "/tc/") : "zh-cn" == n && (t = t.replace("/sc/", "/tc/")) : "zh-cn" == e && ("en" == n ? t = t.replace("/en/", "/sc/") : "zh-hk" == n ? t = t.replace("/tc/", "/sc/") : "zh-cn" == n && (t = t.replace("/sc/", "/tc/"))), checkURLexist(t)) {
        // Remarked by Calvin 21122020
        // Original window.top.location.href = t;
        window.location.href = validateSwapLangURL(t);
        var i = new Date;
        i.setTime(i.getTime() + 31536e6), SetCookie("language", n, i, "/", null, !1)
    } else {
        // Remarked by Calvin 21122020
        // Original var o = window.top.location.href;
        var o = window.location.href;
        if(!notFound){
            o.indexOf("/en/") >= 0 ? alert("English Version Only\n只有英文版") : (o.indexOf("/tc/"), alert("只有中文版\nChinese Version Only"));
        }else{
            window.location.href = validateSwapLangURL(t);
        }
    }
}

// Cookies
function initialCookie() {
    var e = window.location.toString().split("//")[1].split("/"),
        t = e[1].split("/"),
        n = (e[0], t[0]);
    "" == window.name && (window.name = "isdWin");
    var i = location.domain ? location.domain : null,
        o = new Date;
    o.setTime(o.getTime() + 31536e6), "" == n || "en" != n && "zh-hk" != n && "zh-cn" != n ? (null != GetCookie("language") ? SetCookie("language", GetCookie("language"), o, "/", i) : SetCookie("language", "en", o, "/", i), window.location.href = "/" + GetCookie("language") + "/index.html") : SetCookie("language", n, o, "/", i)
}
function GetCookie(e) {
    if ("font-size" == e) {
        if (document.cookie.indexOf(e) < 0) return null;
        var t = document.cookie.indexOf(e) + e.length + 1,
            n = document.cookie.indexOf(";", t);
        return -1 == n && (n = document.cookie.length), decodeURI(document.cookie.substring(t, n))
    }
    var i = document.cookie.match("(^|;)?" + e + "=([^;]*)(;|$)");
    return i ? unescape(i[2]) : null
}
function SetCookie(e, t, n, i, o, r) {
    var s = e + "=" + escape(t);
    s += "; expires=" + n.toGMTString(), i && (s += "; path=" + escape(i)), o && (s += "; domain=" + escape(o)), r && (s += "; secure"), document.cookie = s
    s += "; sameSite=Lax;";
    var getCookie = document.cookie;
    getCookie = s;
    document.cookie = getCookie;
}
if (document.cookie !== null) {
    document.cookie += "; sameSite=Lax;"
}

// get current lang
// console.log(phpLang);
var phpLang = "";
if(phpLang != null){
    langSplit = phpLang.split('-');
    if(langSplit[2]){
        var currentLang = langSplit[1]+'-'+langSplit[2];
    }else{
        var currentLang = langSplit[1];
    }
    // console.log(currentLang);
}else{
    var currentLang = getLang();
    // console.log(currentLang);
}
$(document).mouseup(function (e) {
    var container = $(".modal-content");
})

// header click icon show dropdown modal
$(document).on("click", function (e) {
    var curUrl = window.location.href;
    // var urlParams = new URLSearchParams(window.location.search);
    var paramCalendar = urlParams.get('calendar');
    var paramNotices = urlParams.get('notices');
    // var paramSearch = urlParams.get('search');
    var id = e.target.id.split("-");
    // console.log(e.target.id);
    if($(e.target).is(".btn-close-black")){
        $("#li-search").css("background-image", "none");
        $("#icon-search").css("display", "block");
        $("#close-search").hide();
        $("#li-calendar").css("background-image", "none");
        // if(curUrl.indexOf("?") != -1) {
        //     curUrl = removeURLParameter(curUrl,"calendar");
        //     curUrl = removeURLParameter(curUrl,"search");
        //     window.history.pushState({ path: curUrl }, '', curUrl);
        // }
    }
    if($(e.target).not(".headerModal *")) {
        // console.log(e.target.id);
        // if(!$(".headerModal").is(".show")) {
        //     if(!$(e.target).is(".icon-nav")){
        //     if(!$(e.target).is(".icon-nav-mobi")){

        //     if(!$(e.target).is(".icon-search-mobi")){
        //     }

        //     }
        //     }
        // }
        // if($(e.target).is(".icon-search")){
        //     $("#close-search").show();
        //     // $("#icon-search").hide();
        //     $("#close-nav").hide();
        //     $("#li-nav").css("background-image", "none");
        //     $("#icon-nav").show();
        //     $("#header-nav").modal('hide');
        //     if(paramNotices) {
        //         curUrl = removeURLParameter(curUrl,"notices");
        //         window.history.pushState({ path: curUrl }, '', curUrl);
        //     }
        //     if(curUrl.includes('?')){
        //         var curUrl = curUrl+'&search=y';
        //     }else{
        //         var curUrl = curUrl+'?search=y';
        //     }
        //     if(!paramSearch){
        //         window.history.pushState({ path: curUrl }, '', curUrl);
        //     }
        // }else 
            if($(e.target).is(".icon-nav")){
            $("#close-search").hide();
            $("#li-search").css("background-image", "none");
            $("#icon-search").show();
            $("#header-search").modal('hide');

        }else if($(e.target).is(".icon-nav-mobi")){
            $("#header-search").modal('hide');
            $(window).resize(function() {
                if ($(window).width() > 991) {
                    $("#header-nav").modal('hide');
                    setTimeout(function() {
                        $(window).off('resize');
                    }, 0);
                }
            });
        }else if($(e.target).is(".icon-search-mobi")){
            $("#icon-search").hide();
            $("#close-search").show();
            $("#header-nav").modal('hide');


            // if(curUrl.includes('?')){
            //     var curUrl = curUrl+'&search=y';
            // }else{
            //     var curUrl = curUrl+'?search=y';
            // }
            // if(!paramSearch){
            //     window.history.pushState({ path: curUrl }, '', curUrl);
            // }
            // if(paramSearch){
            //     curUrl = removeURLParameter(curUrl,"search");
            //     window.history.pushState({ path: curUrl }, '', curUrl);
            // }
            // setTimeout(()=>{
            //     $('.header-effect-calendar .day-event').hide();
            //     $('.header-effect-calendar .calendar>.calendar-top').show();
            //     $('.header-effect-calendar .calendar>.weekdays').show();
            //     $('.header-effect-calendar .calendar>.calendar-mobi-2-days').show();
            // }, 200);
        }else if($(e.target).is(".header-mobi-notice-title .btn-close-black")){
            $("#li-search").css("background-image", "none");
        }else if($(e.target).is(".header-mobi-search-title .btn-close-black")){
            $("#li-notice").css("background-image", "none");
        }
        if($('.language-switcher').hasClass('active')&&($('.language-switcher').hasClass('hover')||$('.language-switcher').hasClass('active'))&&!document.querySelector('.language-switcher').contains(e.target)){
            hideLangSwitchContent()
        }
        if($(".sub-menu").hasClass("active")&&!document.querySelector('.sub-menu.active').contains(e.target)){
            $(".sub-menu").removeClass("active");
        }
    }
})
// header icons (calendar/notice/search) display link
var curUrl = window.location.href;
var urlParams = new URLSearchParams(window.location.search);

var paramNotices = urlParams.get('notices');
var paramSearch = urlParams.get('search');
if(paramSearch=="y"){
    $("#icon-search").click();
    $("#close-search").show();
    $("#icon-search").hide();
    $("#close-nav").hide();
    $("#li-nav").css("background-image", "none");
    $("#icon-nav").show();
    $("#header-notice").modal('hide');
    $("#header-nav").modal('hide');
}
// function removeURLParameter(url, parameter) {
//     //prefer to use l.search if you have a location/link object
//     var urlparts = url.split('?');   
//     if (urlparts.length >= 2) {

//         var prefix = encodeURIComponent(parameter) + '=';
//         var pars = urlparts[1].split(/[&;]/g);

//         //reverse iteration as may be destructive
//         for (var i = pars.length; i-- > 0;) {    
//             //idiom for string.startsWith
//             if (pars[i].lastIndexOf(prefix, 0) !== -1) {  
//                 pars.splice(i, 1);
//             }
//         }

//         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
//     }
//     return url;
// }
// $("#close-calendar").click(function() {
//     if(paramCalendar) {
//         curUrl = removeURLParameter(curUrl,"calendar");
//         window.history.pushState({ path: curUrl }, '', curUrl);
//     }
//     if(paramNotices) {
//         curUrl = removeURLParameter(curUrl,"notices");
//         window.history.pushState({ path: curUrl }, '', curUrl);
//     }
//     if(paramSearch) {
//         curUrl = removeURLParameter(curUrl,"search");
//         window.history.pushState({ path: curUrl }, '', curUrl);
//     }
// });

$("#close-search").click(function() {

    if(paramSearch) {
        // curUrl = removeURLParameter(curUrl,"search");
        window.history.pushState({ path: curUrl }, '', curUrl);
    }
});
// Detect Pressed Esc Key
document.onkeydown = function(evt) {
    evt = evt || window.event;
    // if (evt.keyCode == 13) {
    //     // $(".filter-options").css("display", "block");
        
    // }
    if (evt.keyCode == 27) {
        $('html').removeAttr('style');
        $("#close-search").hide();
        $("#li-search").css("background-image", "none");
        $(".language-switcher-content").removeClass("show");
        $(".language-switcher>button.langbtn").attr('aria-expanded',false)
        $(".sub-menu").removeClass("active");
        let navLink=$('ul.navbar-nav>li>a.nav-link');
        navLink.each(function() {
            if($(this).parent().find('.sub-menu').length>0){
                console.log($(this).parent().find('.sub-menu'))
                $(this).attr('aria-expanded','false');
            }
        });


        $('.language-switcher').removeClass('active');
        $('.language-switcher').removeClass('hover');
        $(".navbar-nav>li").removeClass('hover')

        // $(".filter-options").css("display", "none");
        $("#icon-search").show();
        if(paramSearch) {
            curUrl = removeURLParameter(curUrl,"search");
            window.history.pushState({ path: curUrl }, '', curUrl);
        }
    }
};


// scroll to show back to top btn
$(window).scroll(function (event) {
    var scroll = $(window).scrollTop();
    if(scroll > 73) {
        document.querySelector(".btn-top").style.display = "block";
    }else {
        document.querySelector(".btn-top").style.display = "none";
    }
});
// tooltip
if($('[data-toggle="tooltip"]').length>0){
 $('[data-toggle="tooltip"]').tooltip();
}


$(".copyright-year").html(new Date().getFullYear());
$('.current-floor-image').click(function(){
    // console.log($(this).children().attr('src'));
    $(".popup-image-container").html('<img class="popup-floor-image" src="'+$(this).children().attr('src')+'">');
});
// 20220905 click close btn to reset iframe
$('.btn-close').click(function(){      
    $('iframe').attr('src', $('iframe').attr('src'));
});




$(document).ready(function() {

        $('#filter-accordion input[type="checkbox"]').keypress(function (event) {
            var keycode = (event.keyCode ? event.keyCode : event.which);
            if (keycode == 13) {
                $(this).trigger('click');
                event.stopPropagation();
            }
        });
  
  $('.mobile-top-block').find('button.btn-header-nav-back').remove();

    var urlParams = new URLSearchParams(window.location.search);
    // console.log(urlParams);

    // 20221118 show that floor if url contain parameter
    var paramFloor = urlParams.get('floor');
    if(paramFloor){
        handleFloorSelectorClick(paramFloor.toUpperCase()+"-floor");
    }

    $( ".navbar-nav>li>a" ).on("focus", function(e) {
        $('.sub-menu').removeClass('active');
        $('ul.navbar-nav>li>a.nav-link').attr('aria-expanded','false')
        let navlink=$('ul.navbar-nav>li>a.nav-link');
        navlink.each((index)=>{
            if($(navlink[index]).parent().find('.sub-menu').length===0){
                $(navlink[index]).removeAttr('aria-expanded')
            }
        })
        if($(this).parent().find('.sub-menu').length>0){
            $(this).parent().find('.sub-menu').addClass('active');
            $(this).parent().find('>a.nav-link').attr('aria-expanded','true')
        }
    });
    if($('ul.navbar-nav>li:last>.sub-menu').length===0){
        $( ".navbar-nav>li:last>a" ).on("blur", function(e) {
            $('.sub-menu').removeClass('active');
            $('ul.navbar-nav>li>a.nav-link').attr('aria-expanded','false')
            let navlink=$('ul.navbar-nav>li>a.nav-link');
            navlink.each((index)=>{
                if($(navlink[index]).parent().find('.sub-menu').length===0){
                    $(navlink[index]).removeAttr('aria-expanded')
                }
            })
        })
    }else{
        $('ul.navbar-nav>li:last>.sub-menu a:last').on("blur", function(e) {
            setTimeout(() => {
                if(!document.querySelector('ul.navbar-nav > li:last-child > .sub-menu').contains(document.activeElement)&&!$('ul.navbar-nav>li:last').is(":focus")){
                    $('.sub-menu').removeClass('active');
                    $('ul.navbar-nav>li>a.nav-link').attr('aria-expanded','false')
                    let navlink=$('ul.navbar-nav>li>a.nav-link');
                    navlink.each((index)=>{
                        if($(navlink[index]).parent().find('.sub-menu').length===0){
                            $(navlink[index]).removeAttr('aria-expanded')
                        }
                    })   
                }
            }, 0);
            
        })
    }
    $( ".navbar-nav>li>a:first" ).on("blur", function(e) {
        setTimeout(() => {
            if (!$("ul.navbar-nav>li:first>.sub-menu")[0].contains(document.activeElement)) {
                $('.sub-menu').removeClass('active');
                $('ul.navbar-nav>li>a.nav-link').attr('aria-expanded','false')
                let navlink=$('ul.navbar-nav>li>a.nav-link');
                navlink.each((index)=>{
                    if($(navlink[index]).parent().find('.sub-menu').length===0){
                        $(navlink[index]).removeAttr('aria-expanded')
                    }
                })   
            }
        }, 0);
        
    })
    $(".navbar-nav>li").on("mouseenter",function () {
        $(this).addClass("hover")
    }).on("mouseleave",function () {
        $(this).removeClass("hover")
    })
    
    let menuLinks = document.querySelectorAll('.navbar-nav>li');
    menuLinks.forEach(function(link,index) {
        if(link.querySelectorAll('.sub-menu').length>0){
            link.querySelector('a.nav-link').setAttribute('aria-expanded','false');
        }
        link.onmouseenter = function(){
            if(link.querySelectorAll('.sub-menu').length>0){
                link.querySelector('a.nav-link').setAttribute('aria-expanded','true')
            }
        }
        link.onmouseleave = function(e){
            if(link.querySelectorAll('.sub-menu').length>0){
                link.querySelector('a.nav-link').setAttribute('aria-expanded','false')
            }
        }
    });

    $('.pagination-container').attr('aria-label', currentPageLang=='zh-hk'?'分頁':'Pagination');

    //header active link

    if($('.aboutus-content').length>0||$('.aboutus-nearby').length>0||$('.explorer-section').length>0||$('.trip-details').length>0||location.pathname.includes('/visit/')){
        $('.navbar-nav>li')[0].classList.add('active');
    }
    if($('.main-exhitibions').length>0||$('.exhibition-details').length>0){
        $('.navbar-nav>li')[1].classList.add('active');
    }
    if($('.activities-search').length>0||$('.activities-details-block').length>0){
        $('.navbar-nav>li')[2].classList.add('active');
    }
    if($('.collection-details-info').length>0||$('.collection-details-block').length>0||$('.collection-items').length>0||location.pathname.includes('/collections/')){
        $('.navbar-nav>li')[3].classList.add('active');
    }
    if($('.publication-details-popup').length>0||
        $('.publications-listing').length>0||
        $('.pastevents-listing').length>0||
        $('.pastevent-details-block').length>0||
        $('.travelling-listing').length>0||
        $('.e-materials-listing').length>0||
        $('.e-materials-details-block').length>0||
        $('.servicekits-listing').length>0||location.pathname.includes('/resources/')
    )
    {
        $('.navbar-nav>li')[4].classList.add('active');
    }
    if($('.railway-museum').length>0||$('.sheungyiufolk-museum').length>0){
        $('.navbar-nav>li')[5].classList.add('active');
    }

    $('.gallery-btn').on('click',function(){
        $('html').css('overflow-y', 'hidden');
    });
    $('.btn-close').on('click',function(){
        $('html').css('overflow-y', 'auto');
    });
    
    
});

// 20230718 add floor current svg class
function addFloorCurrentSvgClass(){
$(".main-floor-plan-graphic .floor-svg-container").each(function() {
    $(this).removeClass("floor-current-svg");
    // $(this).attr('id', 'floor-current-svg');
    if($(this).children("svg").is(":visible")){
        $(this).addClass("floor-current-svg");
        // $(this).removeAttr('id');
    }
});
}

// 20230720 each click in floor current svg
function getCenterPointAndScaleSVG(id,translateW,translateH){
    $(".floor-current-svg #icons > g#"+id).show();
    var elem = document.getElementById(id);
    // var bBox = elem.getBBox();
    var bBox = document.querySelector(".floor-current-svg svg").getBBox();
    var scaleX = 2;
    var scaleY = 2;
    // console.log(elem);
    // var translateW = parseInt(-bBox.width/3.5);
    // var translateH = parseInt(-bBox.height/3.5);
    var transform = "scale("+scaleX+","+scaleY+") translate("+parseInt(translateW)+"px,"+parseInt(translateH)+"px)";
    // var transform = "scale(1.1,1.1)";
    // console.log(transform);
    $(".floor-current-svg #icons > g#"+id).css("transform", transform);
}

function clickFloorCurrentSvg(){
    $(".floor-current-svg .floor-svg-click").each(function() {
        $(this).on( "mouseover", function() {
            $(this).find("path").not('.svg-gradient').addClass("floor-svg-fill");
            $(this).find("polygon").addClass("floor-svg-fill");
            $(this).find("rect").addClass("floor-svg-fill");
        });
        $(this).on( "click", function() {
            $(".floor-current-svg #icons > g").css("transform", "initial");
            $(".floor-current-svg #icons > g").show();
            $(".floor-current-svg .floor-svg-click").removeClass("floor-svg-fill").removeClass("floor-svg-clicked");
            $(this).addClass("floor-svg-fill").addClass("floor-svg-clicked");
            var svgPopup="",svgTour,svgName,svgDetails,svgDetailsUrl,svgEvent,svgLeft,svgTop;
            // console.log(floorPlanDetails);
            $.each(floorPlanDetails, function( key, value ) {
                // console.log($(this));
                if($(".floor-svg-clicked").hasClass(key)){
                    if(currentLang == "en"){
                        svgName=value.nameEng;
                        svgDetails=value.detailsEng;
                        svgDetailsUrl=value.detailsLinkEng;
                        svgTour=value.tourEng;
                        svgTourUrl=value.tourlinkEng;
                    }else if(currentLang == "zh-cn"){
                        svgName=value.nameChs;
                        svgDetails=value.detailsChs;
                        svgDetailsUrl=value.detailsLinkChs;
                        svgTour=value.tourChs;
                        svgTourUrl=value.tourlinkChs;
                    }else if(currentLang == "zh-hk"){
                        svgName=value.nameCht;
                        svgDetails=value.detailsCht;
                        svgDetailsUrl=value.detailsLinkCht;
                        svgTour=value.tourCht;
                        svgTourUrl=value.tourlinkCht;
                    }
                }

            });
            // if($window <= 1087){
                // if($(this).attr("id") == "f1-restaurant"){
                //     svgLeft="11vw";
                //     svgTop="4vw";
                // }
            // }else{
                // if($(this).attr("id") == "f1-restaurant"){
                    // svgLeft="177px";
                    // svgTop="50px";
                // }else if($(this).attr("id") == "f1-hall"){
                    // svgLeft="295px";
                    // svgLeft="370px";
                    // svgTop="125px";
                // }else if($(this).attr("id") == "f1-spot"){
                    // svgLeft="630px";
                    // svgTop="250px";
                // }else if($(this).attr("id") == "f1-theatre"){
                    // svgLeft="710px";
                    // svgTop="95px";
                // }
            // }
            $(".floor-svg-popup").remove();
            svgPopup += `<div class="floor-svg-popup">
            <div class="floor-svg-popup-name">${svgName}</div>`;
            if(svgTour){
                svgPopup += `<div class="floor-svg-popup-details" data-tour="${svgTour}">
                <a href="#" target="_self" class="floor-video-link" data-bs-toggle="modal" data-bs-target="#floor-plan-image">
                360° Photo
                </a></div>`;
            }
            svgPopup += `
                <div class="floor-svg-popup-details"><a href="${svgDetailsUrl}" target="_self">${svgDetails}</a></div>
            </div>`;

            // $(".floor-current-svg").append(svgPopup);
            $(".svg-popup").append(svgPopup);

            $(".floor-svg-popup").css("left",svgLeft).css("top",svgTop);
            // $(".floor-svg-popup").css("transform","translate3d(625px, 249px, 0px)");
            $(".floor-video-link").click(function() {
                // console.log($(this).parent().data("tour"));
                var item;
                var iframeClass;
                if($(this).parent().data("video")){
                    item = $(this).parent().data("video");
                    iframeClass = "iframe-video";
                }else if($(this).parent().data("tour")){
                    item = $(this).parent().data("tour");
                    iframeClass = "iframe-tour";
                }
                // console.log(item);
                $(".modal-popup .popup-box").html('<iframe class="'+iframeClass+'" src="'+item+'" title="video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>');
            });
        });
    });
    // svg icon click to enlarge scale
    $(".floor-svg-icon-click").each(function() {
        $(this).click(function(){
            $(".floor-svg-popup").remove();
            $(".floor-current-svg #icons > g").hide();
            // console.log($(this).find("img").attr("src"));
            if($(this).find("img").attr("src").indexOf("icon-new_the_spot.png") >= 0){
                // getCenterPointAndScaleSVG("f1-icon-artwork-1",-627,-427);
                // getCenterPointAndScaleSVG("f1-icon-artwork-2",-756,-415);
                getCenterPointAndScaleSVG("f1-icon-spot-1",-834,-423);
            }else if($(this).find("img").attr("src").indexOf("icon-new_baby_caring_room.png") >= 0){
                getCenterPointAndScaleSVG("f1-icon-baby-1",-335,-166);
            }else if($(this).find("img").attr("src").indexOf("icon-new_the_spot.png") >= 0){
                getCenterPointAndScaleSVG("f1-icon-spot-1",-335,-166);
            }else if($(this).find("img").attr("src").indexOf("icon-new_cloak_room.png") >= 0){
                getCenterPointAndScaleSVG("f1-icon-cloakroom-1",-589,-159);
            }else if($(this).find("img").attr("src").indexOf("icon-new_the_mart.png") >= 0){
                getCenterPointAndScaleSVG("f1-icon-mart-1",-503,-159);
                getCenterPointAndScaleSVG("f1-icon-mart-2",-540,-159);
            }else if($(this).find("img").attr("src").indexOf("icon-new_ticketing_machines.png") >= 0){
                getCenterPointAndScaleSVG("f1-icon-ticketing-1",-719,-165);
            }
        });
    });
}

//const govSearchURL="https://gov-dev.suntek.com.hk/jsresult?";
function submitSearch(locale, input, event) { 
	var tmp = document.getElementById(input).value;
	tmp = $.trim(tmp);
	var len = tmp.length;
	var legalChars = /^[\w -]+$/;
	var illegalChars2 = /[\W_]/;
	var illegalChars1 = /[\~\`\@\#\$\%\^\&\*\(\)\_\+\=\|\\\}\{\]\[\'\"\;\:\?\>\<\/]/;

	if (len == 0) {
		if (locale == "zh_TW") alert("您的搜索輸入不正確。");
		else if (locale == "zh_CN") alert("您的搜索输入不正确。");
		else alert("The searching input you entered is not valid.");
		return false;
	} else if (illegalChars1.test(tmp)) {
		if (locale == "zh_TW") alert("您的搜索輸入包含了非法字符。");
		else if (locale == "zh_CN") alert("您的搜索输入包含了非法字符。");
		else alert("The searching input contains illegal characters.");
        event?.preventDefault();
		return false;
	} else {
		
		if (locale == "zh_TW") {
			window.location.href =  window.location.origin + "/tc/search-result.html?query=" + tmp;
		} else if (locale == "zh_CN") {
			window.location.href =  window.location.origin + "/sc/search-result.html?query=" + tmp;
        } else {
            window.location.href =  window.location.origin + "/en/search-result.html?query=" + tmp;
        }
		document.charset = "utf-8";
		//document.frmSearch.submit();
	}
}

function hideLangSwitchContent(params) {
    $('.language-switcher').removeClass('active');
    $('.language-switcher').removeClass('hover');
    $(".language-switcher>button.langbtn").attr('aria-expanded',false)
    $('.language-switcher-content').removeClass('show');
}

$( document ).ready(function() {
    var lastScrollTop = 0, delta = 15;
    $(window).scroll(function(event){
      var st = $(this).scrollTop();
      
      if($('body').hasClass('home')&&($('body').hasClass('monochrome')||$('html').hasClass('monochrome'))){
        delta=60;
      }

      if(Math.abs(lastScrollTop - st) <= delta)
          return;
      
        if ((st > lastScrollTop) && (lastScrollTop>0)) {
            $(".page-head__bottom").addClass("header-hidden");
            $('.inner-page header').css('border-bottom', 'none');
            //   $('header .navbar>div>ul>li>.sub-menu').hide();
        } else {
            $(".page-head__bottom").removeClass("header-hidden");
            $('.inner-page header').css('border-bottom', '1px solid');
        }
      lastScrollTop = st;
    });
  // Select all h2 elements
    
    if ($('.accordion-content').find('h3').length === 0) {
  $(".content-accordion h2.accordionHead").replaceWith(function() {
    return $("<h3>", {
      class: this.className, // Keep existing classes
      id: this.id,           // Keep existing ID
      html: $(this).html()   // Keep the inner HTML content
    });
  });      
    }
  $(".content-accordion h2.accordionHead").replaceWith(function() {
    return $("<h4>", {
      class: this.className, // Keep existing classes
      id: this.id,           // Keep existing ID
      html: $(this).html()   // Keep the inner HTML content
    });
  });
  $(".center-content .accordion-content .content-title").replaceWith(function() {
    return $("<h3>", {
      class: this.className, // Keep existing classes
      id: this.id,           // Keep existing ID
      html: $(this).html()   // Keep the inner HTML content
    });
  });  
  $(".exhibition-details .page-title-block p.section-title").replaceWith(function() {
    return $("<h2>", {
      class: this.className, // Keep existing classes
      html: $(this).html()   // Keep the inner HTML content
    })
  });
  $(".activities-section .page-title-block p.section-title").replaceWith(function() {
    return $("<h2>", {
      class: this.className, // Keep existing classes
      html: $(this).html()   // Keep the inner HTML content
    })
  });  

  $(".activities-section .page-title-block p.section-title").replaceWith(function() {
    return $("<h2>", {
      class: this.className, // Keep existing classes
      html: $(this).html()   // Keep the inner HTML content
    })
  });  

  $(".collection-details-head .page-title-block p.section-title").replaceWith(function() {
    return $("<h2>", {
      class: this.className, // Keep existing classes
      html: $(this).html()   // Keep the inner HTML content
    })
  });   
  
  $(".generic-content.sectionTitle .page-title-block p.section-title").replaceWith(function() {
    return $("<h2>", {
      class: this.className, // Keep existing classes
      html: $(this).html()   // Keep the inner HTML content
    })
  });  
  
  $(".trip-details .page-title-block p.section-title").replaceWith(function() {
    return $("<h2>", {
      class: this.className, // Keep existing classes
      html: $(this).html()   // Keep the inner HTML content
    })
  });   
  $(".collection-detailspage .page-title-block p.section-title").replaceWith(function() {
    return $("<h2>", {
      class: this.className, // Keep existing classes
      html: $(this).html()   // Keep the inner HTML content
    })
  });   
  $(".page-title-block p.section-title").replaceWith(function() {
    return $("<h2>", {
      class: this.className, // Keep existing classes
      html: $(this).html()   // Keep the inner HTML content
    })
  });   
  
  if($('header button.langbtn').length>0){
    $('header button.langbtn').attr('title', currentPageLang === 'zh-hk'?'選擇語言':currentPageLang === 'zh-cn'?'选择语言':'Select Language');
  }

  $('.language-switcher').on( "click", function(e) {
    e.stopPropagation();

    //for activities filter
    if(typeof hideAllFilterOptions!=="undefined"){
        hideAllFilterOptions();
    }

    //for resource page listing-filter
    if(typeof yearBtn!=="undefined"&&typeof yearMenu!=="undefined"&&yearMenu?.classList?.contains('show')){
        toggleDropdown(yearBtn, yearMenu)(e);
    }
    if(typeof categoryBtn!=="undefined"&&typeof categoryMenu!=="undefined"&&categoryMenu?.classList?.contains('show')){
        toggleDropdown(categoryBtn, categoryMenu)(e);
    }

    //self
    $(this).toggleClass("active");
    $('.language-switcher-content').toggleClass('show');
    if($(this).hasClass('active')){
        $(this).find('button.langbtn').attr('aria-expanded',true);
    }else if(!$(this).hasClass('hover')){
        $(this).find('button.langbtn').attr('aria-expanded',false);
    }
  });
  $('.language-switcher').on("mouseenter",function(){
    $(this).find('button.langbtn').attr('aria-expanded',true);
    $(this).addClass('hover');
  }).on("mouseleave",function(){
    if($(this).hasClass('active')){
      $(this).find('button.langbtn').attr('aria-expanded',true);
    }else{
      $(this).find('button.langbtn').attr('aria-expanded',false);
      $(this).removeClass('hover');
    }
  })
  $('.language-switcher-content>a:last').on("keydown",function (e) {
    if (e.key === 'Tab') {
        hideLangSwitchContent();
    }
  })

    if ($( "body" ).hasClass( "home" )) {
        $('header').on( "mouseover", function() {
            //$('header').css('background', 'rgb(255,255,255)');
            //$('.main-nav a').css('color', '#000');
            //$('header a').css('color', '#000');
            //$('header p').css('color', '#000');       
            //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)');
            //$('.langbtn').css('color', '#000');
            //$('.opening-hour').removeClass('open').addClass('opened-white');
            //$('.page-head__top').addClass('head-border');
            // $('.page-head__top').addClass('scrolling-head');
        } );
        $('header').on( "mouseout", function() {
            //$('header').css('background', 'rgb(0,0,0,0.8)');
                // $('.page-head__top').css('background', 'rgb(0,0,0,.8)');
                // $('.page-head__bottom').css('background', 'rgb(0,0,0,.8)');        
            //$('.main-nav a').css('color', '#fff');
            //$('header a').css('color', '#fff');   
            //$('header p').css('color', '#fff');   
            //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(100%) contrast(100%)');
            //$('.opening-hour').removeClass('opened-white').addClass('open');
            //$('.langbtn').removeAttr('style');
            //$('.page-head__top').removeClass('head-border');
            // $('.page-head__top').removeClass('scrolling-head');
            // $('header .navbar .sub-menu a').css('color', '#000');
            // $('header .navbar .sub-menu p').css('color', '#000');
        } );
    } else {
    $('header').on( "mouseover", function() {
        //$('header').css('background', 'rgb(255,255,255)');
        // $('.page-head__bottom').removeClass('header-hidden');     
        //$('.main-nav a').css('color', '#000');
        //$('header a').css('color', '#000');
        //$('header p').css('color', '#000');    
    //   $('.page-head__top').addClass('scrolling-head');
        //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)');
    } );
    $('header').on( "mouseout", function() {
        //$('header').css('background', 'rgb(255,255,255)');   
            // $('.page-head__bottom').addClass('header-hidden');     
        //$('.main-nav a').css('color', '#000');
        //$('header a').css('color', '#000');   
        //$('header p').css('color', '#000');   
    //   $('.page-head__top').removeClass('scrolling-head');
        //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)');
        // $('header .navbar .sub-menu a').css('color', '#000');
        // $('header .navbar .sub-menu p').css('color', '#000');
    } );        
    }
    //$('header .navbar .sub-menu a').css('color', '#000');
    //$('header .navbar .sub-menu p').css('color', '#000');
    $('header .navbar>div>ul>li').css('cursor','pointer');

    // const isTablet = /(ipad|tablet|(android(?!.*mobile))|(windows(?!.*phone)(.*touch))|kindle|playbook|silk|(puffin(?!.*(IP|AP|WP))))/.test(navigator.userAgent.toLowerCase());
    // Check if the primary input mechanism is touch (mobile/tablet)
    const isTouchDevice = () => {return window.matchMedia("(any-pointer:coarse)").matches;};

    if(isTouchDevice()){
        $('.circle').addClass('scale1Important');
    }

    $('.circle').on("mouseover touchstart",function(event){
        if(isTouchDevice()){
            $('.circle').addClass('scale1Important');
        }else{
             $('.circle').removeClass('scale1Important');
        }
        if(event.type === "mouseover" && window.innerWidth > 768&&!isTouchDevice()){
            $(this).addClass('active')
            $('.circle:not(.active)').css('transform', 'scale(0.5)')
        }
        if(event.type === "touchstart" && window.innerWidth > 768&&!isTouchDevice()){
            $(this).addClass('active')
            $('.circle:not(.active)').css('transform', 'scale(0.5)')
        }
    })
    $('.circle').on("mouseout touchend",function(){
        $(this).removeClass('active')
        if(!isTouchDevice()){
            $('.circle:not(.active)').css('transform', '')
        }
    })
});




$(document).on('scroll', function(){
    if ( $(window).scrollTop() > 0) {
        if ($( "body" ).hasClass( "home" )) {
            //$('header').css('background', 'none');
            //$('.page-head__top').css('background', 'rgb(255,255,255)');
            //$('.page-head__bottom').css('background', 'rgb(255,255,255)');
            //$('.main-nav a').css('color', '#000');
            //$('header a').css('color', '#000');
            //$('header p').css('color', '#000');
            //$('.opening-hour').removeClass('open').addClass('opened-white');
            //$('.langbtn').css('color', '#000');
            //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)');
            //$('.page-head__top').addClass('head-border');
            $('.page-head__top').addClass('scrolling-head');
            //$('.icon-search').css('filter','revert');
            $('header')
            .on( "mouseover", function() {
                // $('header').css('background', 'rgb(255,255,255)');
                $('.page-head__bottom').removeClass('header-hidden');
            //$('.page-head__top').css('background', 'rgb(255,255,255)');
            //$('.page-head__bottom').css('background', 'rgb(255,255,255)');                
                //$('.main-nav a').css('color', '#000');
                //$('header a').css('color', '#000'); 
                //$('header p').css('color', '#000');      
                //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)'); 
                //$('.opening-hour').removeClass('open').addClass('opened-white');
                //$('.langbtn').css('color', '#000');
            } );
            $('header')
            .on( "mouseout", function() {
                //$('header').css('background', 'none');
                //$('.page-head__top').css('background', 'rgb(255,255,255)'); 
                $('.page-head__bottom').addClass('header-hidden');   
                //$('.page-head__bottom').css('background', 'none');            
                //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)');
                //$('.opening-hour').removeClass('open').addClass('opened-white');
                //$('.main-nav a').css('color', '#000');
                //$('header a').css('color', '#000');   
                //$('header p').css('color', '#000');   
                //$('.langbtn').css('color', '#000');
                //$('.page-head__top').addClass('head-border');
            } );    
        } else {
            //$('header').css('background', 'none');
            //$('.page-head__top').css('background', 'rgb(255,255,255)');
            //$('.page-head__bottom').css('background', 'rgb(255,255,255)');
          $('.page-head__top').addClass('scrolling-head');
            $('header').on( "mouseover", function() {
                //$('header').css('background', 'rgb(255,255,255)');
                //$('header').css('border-bottom', '1px solid');
                $('.page-head__bottom').removeClass('header-hidden');     
                //$('.main-nav a').css('color', '#000');
                //$('header a').css('color', '#000');
                //$('header p').css('color', '#000');   
              
                //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)');
            } );
            $('header').on( "mouseout", function() {
                //$('header').css('background', 'transparent');   
                //$('header').css('border-bottom', 'none');
                    $('.page-head__bottom').addClass('header-hidden');     
                //$('.main-nav a').css('color', '#000');
                //$('header a').css('color', '#000');   
                //$('header p').css('color', '#000');   
                //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)');
            } );              
        }

    } else {
        if ($( "body" ).hasClass( "home" )) {
            //$('header').css('background', 'rgb(0,0,0,0.8)');
            //$('.page-head__top').css('background', 'transparent');
            //$('.page-head__bottom').css('background', 'transparent');               
            //$('.main-nav a').css('color', '#fff');
            //$('header a').css('color', '#fff');
            //$('header p').css('color', '#fff');        
            //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(100%) contrast(100%)');        
            //$('.opening-hour').removeClass('opened-white').addClass('open');
            //$('.langbtn').css('color', '#fff');
            //$('.page-head__top').removeClass('head-border');
            $('.page-head__top').removeClass('scrolling-head');
            $('.icon-search').removeAttr('style');
            $('header')
            .on( "mouseover", function() {
              //$('header').css('background', 'rgb(255,255,255)');
              //$('.main-nav a').css('color', '#000');
              //$('header a').css('color', '#000');
              //$('header p').css('color', '#000');
              //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)');
              //$('.opening-hour').removeClass('opened').addClass('opened-white');
              //$('.langbtn').css('color', '#000');
              //$('.page-head__top').addClass('head-border');
              $('.page-head__top').addClass('scrolling-head');
            } );
            $('header')
            .on( "mouseout", function() {
              //$('header').css('background', 'rgb(0,0,0,0.8)');
            //$('.page-head__top').css('background', 'transparent'); 
            $('.page-head__bottom').removeClass('header-hidden');            
            //$('.page-head__bottom').css('background', 'transparent');               
              //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(100%) contrast(100%)');
              //$('.opening-hour').removeClass('opened-white').addClass('open');
              //$('.main-nav a').css('color', '#fff');
              //$('header a').css('color', '#fff');
              //$('header p').css('color', '#fff');
              //$('.langbtn').css('color', '#fff');
              //$('.page-head__top').removeClass('head-border');
              $('.page-head__top').removeClass('scrolling-head');
            } ); 
        } else {
            //$('header').css('background', 'none');
            //$('.page-head__top').css('background', 'rgb(255,255,255)');
            //$('.page-head__bottom').css('background', 'rgb(255,255,255)');
            $('.page-head__bottom').removeClass('header-hidden');  
            //$('header').css('border-bottom', '1px solid');   
          $('.page-head__top').removeClass('scrolling-head');
            $('header').on( "mouseover", function() {
                //$('header').css('background', 'rgb(255,255,255)');
                //$('header').css('border-bottom', '1px solid');
                // $('.page-head__bottom').removeClass('header-hidden');     
                //$('.main-nav a').css('color', '#000');
                //$('header a').css('color', '#000');
                //$('header p').css('color', '#000');       
                //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)');
            } );
            $('header').on( "mouseout", function() {
                //$('header').css('background', 'transparent');   
                //$('header').css('border-bottom', '1px solid');
                // $('header').css('border-bottom', 'none');   
                    $('.page-head__bottom').removeClass('header-hidden');    
                //$('.main-nav a').css('color', '#000');
                //$('header a').css('color', '#000');   
                //$('header p').css('color', '#000');   
                //$('.header-logo').css('filter', 'invert(0%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(0%) contrast(100%)');
            } );               
        }
    }
});
$(document).ready(function(){
    // $('#dropdown-nav').on('click', function(e) {
    //     e.preventDefault();  // Blocks href="#" jump/scroll-to-top
    //     e.stopPropagation(); // Optional: Prevents bubbling if nested in dropdowns

    //     // Bootstrap will still handle the modal via data attributes—no need to manually trigger
    // });

    // // Optional: Preserve/restore scroll position explicitly (if the above isn't enough)
    // $('#header-nav').on('show.bs.modal', function() {
    //     $(this).data('scrollTop', $(window).scrollTop());  // Store current scroll
    // });
    $('.floor-plan-popup').on('show.bs.modal', function() {
        $('html').css('overflow-y','hidden');
    });

    $('#header-nav').on('hidden.bs.modal', function() {
    //     const scrollTop = $(this).data('scrollTop') || 0;
    //     $(window).scrollTop(scrollTop);  // Restore scroll on close
        $(window).off('resize');
    });  
    vtmLinkConfig();
    // $('.gallery-btn')startsWith('zh')?(currentPageLang==='zh-hk'?'今天閉館':'今天闭馆'):'Closed today';
    // $('.listing-page .page-title-block').removeClass('d-none');
    // $('.listing-page .page-title-block .page-title').removeClass('sr-only');
    $(".gallery-btn .sr-only").text(currentPageLang.startsWith('zh-hk')?'開啟相簿':currentPageLang.startsWith('zh')?"开启相簿":'Open Gallery');
    $(".gallery-btn").attr('aria-label',currentPageLang.startsWith('zh-hk')?'開啟相簿':currentPageLang.startsWith('zh')?"开启相簿":'Open Gallery');
    $(".btn-close").attr('aria-label', currentPageLang.startsWith('zh-hk')?'關閉':currentPageLang.startsWith('zh')?'关闭':'Close');
  	$(".vtm-link").attr("data-bs-target", "#vtm-popup");
    
    const vtmText = currentPageLang.startsWith('zh')?(currentPageLang==='zh-hk'?'最新入場狀態':'最新入场状态'):'Latest Admission Status';
    $(".page-head__right .vtm-link").hover(
        function() {
            $(this).addClass('dim');
            $(this).html('<p>'+vtmText+'</p>');
        },
        function() {
            $(this).removeClass('dim');
            $(this).html('<img src="/assets/img/icon/vtm-black.png" alt="'+vtmText+'">');
        }
    );    
 
    $(".gallery-btn .sr-only").text(currentPageLang.startsWith('zh')?'開啟相簿':'Open Gallery');
    $(".gallery-btn").attr('aria-label',currentPageLang.startsWith('zh')?'開啟相簿':'Open Gallery');
    $(".btn-close").attr('aria-label', currentPageLang.startsWith('zh')?'關閉':'Close');
  	$(".vtm-link").attr("data-bs-target", "#vtm-popup");
    
    $('.anchor-btn').click(function(){
        const accordBarId = $(this).attr("data-id");
        $('#'+accordBarId+' .accordion-button').removeClass('collapsed');
        $('#'+accordBarId+' .accordion-button').attr('aria-expanded', 'true');
        $('[aria-labelledby="'+accordBarId+'"]').addClass('show');

    });

    $('.navbar-toggler').click(function(){
        $('.navbar-collapse').slideToggle(300);
    });
    
    // smallScreenMenu();
    let temp;
    // function resizeEnd(){
    //     smallScreenMenu();
    // }
  
    // $(window).resize(function(){
    //     clearTimeout(temp);
    //     temp = setTimeout(resizeEnd, 100);
    //     resetMenu();
    // });  
    // $('#tag-options label').click(function() {
    //     $(this).addClass("active");
    //   }) 

  });
  
  
//   const subMenus = $('.sub-menu');
//   const menuLinks = $('.nav-link');
  
//   function smallScreenMenu(){
//     if($(window).innerWidth() <= 992){
//         menuLinks.each(function(item){
//             $(this).click(function(){
//                 $(this).next().slideToggle();
//             });
//         });
//     } else {
//         menuLinks.each(function(item){
//             $(this).off('click');
//         });
//     }
//   }
  
//   function resetMenu(){
//     if($(window).innerWidth() > 992){
//         subMenus.each(function(item){
//             $(this).css('display', 'none');
//         });
//     }
//   }

  var footerswiper = new Swiper(".footslide", {
    slidesPerView: 3,
    centeredSlides: false,
    slidesPerGroupSkip: 3,
    grabCursor: true,
    spaceBetween : 0,
    keyboard: {
      enabled: true,
    },
    breakpoints: {
      769: {
        slidesPerView: 8,
        slidesPerGroup: 8,
      },
    },
    navigation: {
      nextEl: ".foot-button-next",
      prevEl: ".foot-button-prev",
    },
  });
  
$(".image-video-link").click(function() {
    // console.log($(this).parent().data("video"));
    $(".modal-popup .popup-box").html('<iframe class="image-video" src="'+$(this).parent().data("video")+'" title="video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>');
    $("#btn-close-slider-video").on("click", function() {
        // Code to execute when the element is clicked
        $(".modal-popup .popup-box").html('');
        $("#btn-close-slider-video").off("click");
    });
});

$(".popup-content-link").click(function() {
    // console.log($(this).parent().data("video"));
    $(".modal-popup .popup-box").html('<iframe class="image-video" src="'+$(this).parent().data("video")+'" title="video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>');
});

// VTM Section
function vtmLinkConfig() {
  let currentLang = getLang();
  if(currentLang == "en"){
  $(".vtm-lightbox").attr('data-video', '/vtm.html');
}else if(currentLang == "zh-hk"){
  $(".vtm-lightbox").attr('data-video', '/vtm.html?lang=tc');
}else if(currentLang == "zh-cn"){
  $(".vtm-lightbox").attr('data-video', '/vtm.html?lang=sc');
} else {
  $(".vtm-lightbox").attr('data-video', '/vtm.html?lang=tc');
}



$(".vtm-link").click(function() {
    let currentLang = getLang();
    let closeAriaLabel= currentLang == "zh-hk" ? '關閉' : currentLang == "zh-cn" ? '关闭' : 'Close'

    // console.log($(this).parent().data("video"));
    $("#vtm-popup.modal-popup .popup-box").html('<button type="button" id="btn-close-slider-video" class="btn-close" data-bs-dismiss="modal" aria-label="'+closeAriaLabel+'"></button><iframe class="image-video vtm-popup" src="'+$(this).parent().data("video")+'" title="video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>');
    $("#btn-close-slider-video").on("click", function() {
        // Code to execute when the element is clicked
        $(".modal-popup .popup-box").html('');
        $("#btn-close-slider-video").off("click");
    });
});
}


// Function to set active class based on current page
function setActiveNavLink() {
    // Get the current page's filename (e.g., 'publicationsouvenir_details.html')
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    // Select all nav links (desktop and mobile)
    const navLinks = document.querySelectorAll('.nav-link, .dropdown-item');
    
    // Remove active class from all links
    navLinks.forEach(link => link.classList.remove('active'));
    
    // Add active class to the matching link
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && (href === currentPage || href.endsWith('/' + currentPage))) {
            link.classList.add('active');
        }
    });
}

// Run on page load
document.addEventListener('DOMContentLoaded', setActiveNavLink);

// Opening Hour
// ------------------------------------------------------------
        // 1. Language detection
        // ------------------------------------------------------------
        const currentPageLang = document.querySelector('html').getAttribute('lang') || 'en';

        // ------------------------------------------------------------
        // 2. Current HKT date / time
        // ------------------------------------------------------------
        function getCurrentHKT(){
            const now = new Date();
            const utc = now.getTime() + now.getTimezoneOffset()*60000;
            const hkt = new Date(utc + 8*60*60000);
            return {
                date: hkt.toISOString().split('T')[0],
                dayOfWeek: hkt.getDay(),
                hours: hkt.getHours(),
                minutes: hkt.getMinutes()
            };
        }

        // ------------------------------------------------------------
        // 3. Parse “10:10 AM” → minutes since midnight
        // ------------------------------------------------------------
        function parseTime(str){
            if(!str||str.trim()==='Closed') return null;
            try{
                const [t,p]=str.trim().split(' ');
                const [h,m]=t.split(':').map(Number);
                let hh=h;
                if(p==='PM'&&h!==12) hh+=12;
                if(p==='AM'&&h===12) hh=0;
                return hh*60+(m||0);
            }catch(e){console.warn('Bad time:',str);return null;}
        }

        // ------------------------------------------------------------
        // 4. Format a single time
        // ------------------------------------------------------------
        function formatTime(str,loc){
            if(str==='Closed') return loc.startsWith('zh')?(currentPageLang==='zh-hk'?'今天閉館':'今天闭馆'):'Closed today';
            try{
                const [t,p]=str.split(' ');
                const [h,m]=t.split(':').map(Number);
                if(loc.startsWith('zh')){
                    const pMap={AM:'上午',PM:'下午'};
                    const pStr=pMap[p];
                  	const hourText=(loc==='zh-hk')?'時':'时';
                    return m===0? `${pStr} ${h} ${hourText}` : `${pStr} ${h} ${hourText} ${m} 分`;
                }
                const min=m===0?'':`:${m.toString().padStart(2,'0')}`;
                return `${h}${min}${p==='AM'?'am':'pm'}`;
            }catch(e){return loc.startsWith('zh')?(currentPageLang==='zh-hk'?'今天閉館':'今天闭馆'):'Closed today';}
        }

        // ------------------------------------------------------------
        // 5. Format whole range
        // ------------------------------------------------------------
        function formatHours(range,loc){
            if(range==='Closed') return loc.startsWith('zh')?(currentPageLang==='zh-hk'?'今天閉館':'今天闭馆'):'Closed today';
            try{
                const [o,c]=range.split('-').map(s=>s.trim());
                return `${formatTime(o,loc)}${currentPageLang.startsWith('zh') ? '至' : ' - '}${formatTime(c,loc)}${currentPageLang.startsWith('zh')?(currentPageLang==='zh-hk'?'開館':'开馆'):''}`;
            }catch(e){return loc.startsWith('zh')?(currentPageLang==='zh-hk'?'今天閉館':'今天闭馆'):'Closed today';}
        }

        // ------------------------------------------------------------
        // 6. Is the venue open right now?
        // ------------------------------------------------------------
        function isBusinessOpen(range,curH,curM){
            if(range==='Closed') return false;
            try{
                const [o,c]=range.split('-').map(s=>s.trim());
                const open=parseTime(o), close=parseTime(c);
                if(open===null||close===null) return false;
                const now=curH*60+curM;
                return now>=open && now<=close;
            }catch(e){return false;}
        }

        // ------------------------------------------------------------
        // 7. Fetch the JSON
        // ------------------------------------------------------------
        fetch('/include/json/opening_hours.json')
            .then(r=>{if(!r.ok) throw new Error('Network'); return r.json();})
            .then(data=>{

                const groups          = data.groups          || [];
                const specialDates    = data.specialDates    || {};
                const publicHolidays  = data.publicHolidays  || [];

                const {date:todayDate, dayOfWeek, hours:curH, minutes:curM}=getCurrentHKT();

                // ------------------------------------------------------------
                // 8. Determine which group applies today (priority order)
                // ------------------------------------------------------------
                let todayGroup = null;
                let todayHours = null;
                let todayDisplayTime = null;     // formatted: "上午10:10至下午8:00"

                // 1. Urgent closure – highest priority
                const urgentGroup = groups.find(g=>g.applicableDays.type==='special_close_dates');

                if(urgentGroup && urgentGroup.applicableDays.dates){

                    const idx = urgentGroup.applicableDays.dates.indexOf(todayDate);

                    if(idx !== -1){

                        todayGroup = urgentGroup;

                        todayHours = urgentGroup.applicableDays.times?.[idx] || 'Closed';

                        todayDisplayTime = formatHours(todayHours, currentPageLang);

                    }

                }
                // 2. Special dates
                if(!todayGroup && specialDates[todayDate]){
                    todayGroup = groups.find(g=>g.applicableDays.type==='special_dates');
                    todayHours = specialDates[todayDate];
                }
                // 3. Public holiday
                if(!todayGroup && publicHolidays.includes(todayDate)){
                    todayGroup = groups.find(g=>g.applicableDays.type==='weekend_and_holidays');
                    todayHours = todayGroup ? todayGroup.time : 'Closed';
                }
                // 4. Weekday / weekend / Tuesday
                if(!todayGroup) {
                    for(const g of groups){
                        const days = g.applicableDays.days;
                        const type = g.applicableDays.type;
                        if(type==='weekdays' && days.includes(dayOfWeek)){
                            todayGroup=g; todayHours=g.time; break;
                        }
                        if(type==='weekend_and_holidays' && days.includes(dayOfWeek)){
                            todayGroup=g; todayHours=g.time; break;
                        }
                        if(type==='specific_day' && g.applicableDays.day===dayOfWeek){
                            todayGroup=g; todayHours=g.time; break;
                        }
                    }
                }

                // fallback
                if(!todayGroup) todayGroup = groups[0] || {};
                if(!todayHours) todayHours = 'Closed';
                // if(!todayTimeLabel) todayTimeLabel = todayGroup.timeLabel?.[currentPageLang] || todayGroup.timeLabel?.en || formatHours(todayHours, currentPageLang);
                if(!todayDisplayTime) todayDisplayTime = formatHours(todayHours, currentPageLang);

                // ------------------------------------------------------------
                // 9. #opening-hours – use timeLabel from the active group
                // ------------------------------------------------------------
                const ohDiv=document.getElementById('opening-hours');
                if(ohDiv){
                    // const timeLabel = todayGroup.timeLabel?.[currentPageLang] || todayGroup.timeLabel?.en || formatHours(todayHours, currentPageLang);
                    // const open = isBusinessOpen(todayHours, curH, curM);
                    // const prefix = currentPageLang.startsWith('zh') ? '今天' : 'Open today ';
                    // ohDiv.textContent = open ? `${prefix}${todayDisplayTime}` : todayDisplayTime;
                    // ohDiv.className = open ? 'open' : 'closed';
const open = todayHours !== 'Closed';
                    const prefix = currentPageLang.startsWith('zh') ? '今天' : 'Open today: ';
                    ohDiv.textContent = open ? `${prefix}${todayDisplayTime}` : todayDisplayTime;
                    ohDiv.className = open ? 'open' : 'closed';                    
                }

                // ------------------------------------------------------------
                // 10. Page title
                // ------------------------------------------------------------
                const title=document.getElementById('open-today-title');
                if(title) title.textContent=currentPageLang.startsWith('zh')?'今天開放時間':'Open today';

                // ------------------------------------------------------------
                // 11. Full schedule (optional)
                // ------------------------------------------------------------
                const list=document.getElementById('grouped-hours-list');
                if(!list) return;

                let html='';

                groups.forEach(g=>{

                    const label = g.dateLabel[currentPageLang] || g.dateLabel.en || '—';
                    const baseTimeLabel = g.timeLabel?.[currentPageLang] || g.timeLabel?.en || '—';

                    // ----- skip empty urgent closure -----
                    // if(g.applicableDays.type==='special_close_dates' && (!g.applicableDays.dates || g.applicableDays.dates.length===0)){
                    //     return;
                    // }

                    // ----- URGENT CLOSURE -----
                    if(g.applicableDays.type==='special_close_dates' && g.applicableDays.dates && g.applicableDays.dates.length>0){
                        return;
                    }

                    // ----- SPECIAL DATES -----
                    if(g.applicableDays.type==='special_dates'){
                        const uniq=[...new Set(Object.values(specialDates))];
                        uniq.forEach(t=>{
                            const isToday = specialDates[todayDate]===t;
                            html+=`<li>
                                      <div class="label">${label}</div>
                                      <div class="time">
                                      ${baseTimeLabel}
                                          ${isToday ? `<span class="today-tag">${currentPageLang.startsWith('zh') ? '今天' : 'Today'}</span>` : ''}
                                      </div>
                                    </li>`;
                        });
                        return;
                    }

                    // ----- ALL OTHER GROUPS -----
                    const isToday = g===todayGroup;
                    html+=`<li>
                              <div class="label">${label}</div>
                              <div class="time">
                                  ${baseTimeLabel}
                                  ${isToday ? `<span class="today-tag">${currentPageLang.startsWith('zh') ? '今天' : 'Today'}</span>` : ''}
                              </div>
                            </li>`;
                });

                list.innerHTML=html;
            })
            .catch(err=>{
                console.error('Opening-hours JSON error:',err);
                const oh=document.getElementById('opening-hours');
                if(oh){
                    oh.textContent=currentPageLang.startsWith('zh')?'無法載入開放時間':'Error loading opening hours.';
                    oh.className='closed';
                }
            });
	
//start of floor plan js
let floorInt=0;
let zoomScale=1;//zoomScale increase when zoomin, zoomScale decrease when zoomout
let svgPanZoom;
let floorPlanData;
let isFirstZoomIn=true;
let floorObj={
    en:[{label:"2/F",value:2},{label:"1/F",value:1},{label:"G/F",value:0}],
    tc:[{label:"2樓",value:2},{label:"1樓",value:1},{label:"地下",value:0}],
    sc:[{label:"2楼",value:2},{label:"1楼",value:1},{label:"地下",value:0}]
}
$(".floor-plan-link").on("click",function(){
    let currentLang = getLang();
    floorInt=0;
    zoomScale=1
    //clear
    $(".floor-plan-popup .HM-logo").html('');
    $(".floor-plan-popup .top-transprant-background").html('');
    $(".floor-plan-popup .Back").html('');
    $(".floor-plan-popup .map").html('');
    $(".floor-plan-popup .left-transprant-background").html('');
    $(".floor-plan-popup .left-floor-button-group").html('');
    $(".floor-plan-popup .pan-button-group").html('');
    $(".floor-plan-popup .zoom-button-group").html('');
    $(".floor-plan-popup .floor-plan-menu").html('');
    $(".floor-plan-popup .floor-plan-detail-sidebar").remove()
    //add
    setTimeout(() => {
        let HMLogo=$(".modal-popup .popup-box .floor-plan-container .floor-plan .HM-logo");
        HMLogo.html(`<picture>
            <source srcset="/assets/img/svg/mobile/HM-logo.svg" media="(max-width: 768px)" />
            <img src="/assets/img/svg/desktop/HM-logo.svg" alt="HM-logo"/>
            </picture>`);
        // $.get("/assets/img/svg/Back.svg",(data)=>{
        //     let Back=$(".modal-popup .popup-box .floor-plan-container .floor-plan .Back");
        //     Back.html(new XMLSerializer().serializeToString(data));
        //    
        // });
        let backToSiteButtonText="Back to site";
        if(currentLang==="zh-hk"){
            backToSiteButtonText="返回網站";
        }else if(currentLang==="zh-cn"){
            backToSiteButtonText="返回网站";
        }
        $(".modal-popup .popup-box .floor-plan-container .floor-plan .Back").html(`<button onclick='closeFloorPlanPopup()'>${backToSiteButtonText}</button>`);
        // $.get("/assets/img/svg/English.svg",(data)=>{
        //     let English=$(".modal-popup .popup-box .floor-plan-container .floor-plan .English");
        //     English.html(new XMLSerializer().serializeToString(data));
        // });
        floorInt=0;
        loadFloorButton();
        loadZoomInOutButton();
        loadPanButton();
        oldWindowWidth=window.innerWidth
        floorInt=0;
        loadSvgFloorPlan(0)
    }, 500);
})
const closeFloorPlanPopup=()=>{
    $('.floor-plan-popup').modal('toggle');
    $('html').css('overflow-y', 'auto');
}
const loadFloorButton=()=>{
    //left floor button
    let currentLang = getLang();
    const leftFloorButtonGroup=$(".modal-popup .popup-box .floor-plan-container .floor-plan .left-floor-button-group");
    leftFloorButtonGroup.html('');
    let langKey=currentLang;
    if(langKey==="zh-cn"){
        langKey="sc";
    }
    if(langKey==="zh-hk"){
        langKey="tc";
    }
    floorObj[langKey].map(({value,label},index)=>{
        let buttonHtml='';      
        buttonHtml=`<button style='top: calc(50% - ${(value-1)*70}px);'`
        if(window.innerWidth<=768||window.innerHeight<528){
             buttonHtml=`<button style='top: calc(50% - ${(value-1)*52}px);'`
        }
        buttonHtml+=` onclick="closeViewDetailSidebar();zoomScale=1;floorInt=${value};loadZoomInOutButton();loadSvgFloorPlan(${value});leftFloorButtonActive(${value},this);">${label}</button>`;
        leftFloorButtonGroup.append(buttonHtml);
    })
    leftFloorButtonActive(floorInt,$(".modal-popup .popup-box .floor-plan-container .floor-plan .left-floor-button-group>button")[2-floorInt]);
}
const zoomInFunc=()=>{
    let isMobile=(window.innerWidth<=768||window.innerHeight<528)?true:false;
    if(isMobile){
        if(zoomScale>=0.55) return;
    }else{
        if(zoomScale>1.25) return;
    }
    if(svgPanZoom){
        if(isMobile){
            zoomScale+=0.45;
        }else{
            zoomScale+=0.25;
        }
        zoomScale=parseInt(zoomScale*100)/100;
        if(isMobile){
            if(zoomScale===1||zoomScale===0.55){
                // $('g#icon-zoom-in>line').attr('stroke','#d4d4d4');
                $('.zoom-in').css('color','#d4d4d4');
                $('.zoom-in').attr('disabled',true);
            }
        }else{
            if(zoomScale===1.5){
                // $('g#icon-zoom-in>line').attr('stroke','#d4d4d4');
                $('.zoom-in').css('color','#d4d4d4');
                $('.zoom-in').attr('disabled',true);
            }
        }
        // $('g#icon-zoom-out>line').attr('stroke','#000000');
        $('.zoom-out').css('color','#000000');
        $('.zoom-out').attr('disabled',false);
        // const {x,y}=svgPanZoom.getViewBox();
        let floorPlanMap=$(".modal-popup .popup-box .floor-plan-container .floor-plan .map");
        const width=floorPlanMap.width();
        const height=floorPlanMap.height();
        let times=(100-Math.sqrt(zoomScale*100)+Math.sqrt(1*100))/100;
        if(isMobile){
            if(zoomScale===0.1){
            }
            if(zoomScale===0.55){
                // svgPanZoom.setViewBox(svgPanZoom.getViewBox().x*1.45,svgPanZoom.getViewBox().y*1.45,1725,1150,100)
                svgPanZoom.setViewBox(svgPanZoom.getViewBox().x*1.625,svgPanZoom.getViewBox().y*1.625,1200,800,100)
            if(width>=668){
                //default +230px limit width
                // svgPanZoom.limits.x2=svgPanZoom.getViewBox().width+230
                svgPanZoom.limits.x2=svgPanZoom.getViewBox().width+520
            }else{
                //default +230px limit width plus
                //every 50px width decrease, every 70px limit width increase
                // svgPanZoom.limits.x2=svgPanZoom.getViewBox().width+230+(668-width)*70/50
                svgPanZoom.limits.x2=svgPanZoom.getViewBox().width+520+(668-width)*50/50
            }
            if((height*2)>=900){
                //default +150px limit height
                // svgPanZoom.limits.y2=svgPanZoom.getViewBox().height+150
                svgPanZoom.limits.y2=svgPanZoom.getViewBox().height+350
            }
}
        }else{
            svgPanZoom.zoomIn();
            if(zoomScale===1){
                svgPanZoom.limits.x2=(1200+(1200-width))+(isFirstZoomIn===true?0:-20)
                svgPanZoom.limits.y2=(800+(800-height))
            }
            if(zoomScale===1.25){
                if(width>=1000){
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-40
                    svgPanZoom.limits.y2=(800+(800-height))*times-20
                }else if(width>=800){
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-55
                    svgPanZoom.limits.y2=(800+(800-height))*times-20
                }else{
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-130
                    svgPanZoom.limits.y2=(800+(800-height))*times-20
                }
                if(height<600){
                    svgPanZoom.limits.y2=(800+(800-height))*times-30
                }
            }
            if(zoomScale===1.5){
                if(width>=1000){
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-80
                    svgPanZoom.limits.y2=(800+(800-height))*times-15
                }else if(width>=800){
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-95
                    svgPanZoom.limits.y2=(800+(800-height))*times-15
                }else{
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-190
                    svgPanZoom.limits.y2=(800+(800-height))*times-15
                }
                if(height<600){
                    svgPanZoom.limits.y2=(800+(800-height))*times-70
                }
            }
        }
        //prevent over limit x when zoom in
        let svgPanZoomViewBox=svgPanZoom.getViewBox();
        if((svgPanZoomViewBox.x+svgPanZoomViewBox.width)>svgPanZoom.limits.x2){
            setTimeout(()=>svgPanZoom.panRight((svgPanZoomViewBox.x+svgPanZoomViewBox.width)-svgPanZoom.limits.x2, 100),300)
        }
        if(svgPanZoomViewBox.x===0){
            setTimeout(()=>{svgPanZoom.panLeft(0,100),300});
        }
    }
}
const loadZoomInOutButton=()=>{
    isFirstZoomIn=true;
    // let svgPath="/assets/img/svg/desktop/button-zoom-in-or-out.svg";
    if (window.innerWidth<=768||window.innerHeight<528){
        // svgPath="/assets/img/svg/mobile/buttons-zoom-in-or-out(mobile).svg";
        // svgPath="/assets/img/svg/desktop/button-zoom-in-or-out.svg";
    }

    const zoomInAriaLabel=currentPageLang === 'zh-hk' ? '放大' : currentPageLang === 'zh-cn' ? '放大' : 'Zoom In';
    const zoomOutAriaLabel=currentPageLang === 'zh-hk' ? '縮小' : currentPageLang === 'zh-cn' ? '缩小' : 'Zoom Out';
    let zoomButton="<button class='zoom-in' aria-label='"+zoomInAriaLabel+"'>+</button><button class='zoom-out' aria-label='"+zoomOutAriaLabel+"'>-</button>"
    let zoomButtonGroup=$(".modal-popup .popup-box .floor-plan-container .floor-plan .zoom-button-group");
    // zoomButtonGroup.html(new XMLSerializer().serializeToString(data));
    zoomButtonGroup.html(zoomButton)
    if(zoomScale===1){
        // $('g#icon-zoom-out>line').attr('stroke','#d4d4d4');
        $('.zoom-out').css('color','#d4d4d4');
        $('.zoom-out').attr('disabled',true);
        // $('g#icon-zoom-in>line').attr('stroke','#000000');
        $('.zoom-in').css('color','#000000');
        $('.zoom-in').attr('disabled',false);
    }else{
        // $('g#icon-zoom-in>line').attr('stroke','#d4d4d4');
        $('.zoom-in').css('color','#d4d4d4');
        $('.zoom-in').attr('disabled',true);
        // $('g#icon-zoom-out>line').attr('stroke','#000000');
        $('.zoom-out').css('color','#000000');
        $('.zoom-out').attr('disabled',false);
    }
    // x2:isMobile?(1200+(1200-width)):(1200+(1200-width)),//isMobile?(675+(675-width)):(1200+(1200-width)),
    // y2:isMobile?(800+(800-height)):(800+(800-height))//isMobile?(450+(450-height)):(800+(800-height))
    //let floorPlanMap=$(".modal-popup .popup-box .floor-plan-container .floor-plan .map");
    // const width=floorPlanMap.width();
    // const height=floorPlanMap.height();
    //svgPanZoom.setViewBox(x, y, width, height, animationTime)
    
    $(".zoom-in").off("click");
    $(".zoom-in").on("click",zoomInFunc);
    $(".zoom-out").off("click");
    $(".zoom-out").on("click",zoomOutFunc);
}
const zoomOutFunc=(isUnSelectItem=false)=>{
    isFirstZoomIn=false;
    let isMobile=(window.innerWidth<=768||window.innerHeight<528)?true:false;
    if(isMobile){
        if(zoomScale===0.1) return;
    }else{
        if(zoomScale===1) return;
    }
    if(svgPanZoom){
        if(isMobile){
            zoomScale-=0.45;    
        }else{
            zoomScale-=0.25;
        }
        zoomScale=parseInt(zoomScale*100)/100;
        
        if(isMobile){
            if(zoomScale===0.1){
                // $('g#icon-zoom-out>line').attr('stroke','#d4d4d4');
                $('.zoom-out').css('color','#d4d4d4');
                $('.zoom-out').attr('disabled',true);
            }
        }else{
            if(zoomScale===1){
                // $('g#icon-zoom-out>line').attr('stroke','#d4d4d4');
                $('.zoom-out').css('color','#d4d4d4');
                $('.zoom-out').attr('disabled',true);
            }
        }
        // $('g#icon-zoom-in>line').attr('stroke','#000000');
        $('.zoom-in').css('color','#000000');
        $('.zoom-in').attr('disabled',false);
        let floorPlanMap=$(".modal-popup .popup-box .floor-plan-container .floor-plan .map");
        const width=floorPlanMap.width();
        const height=floorPlanMap.height();
        let times=(100-Math.sqrt(zoomScale*100)+Math.sqrt(1*100))/100;
        if(isMobile){
            if(zoomScale===0.1){
                //this row could make setViewBox height set correctly
                if(width>436){
                    svgPanZoom.limits.y2=svgPanZoom.getViewBox().height+1300
                    svgPanZoom.limits.x2=svgPanZoom.getViewBox().width+1950
                }else{
                    svgPanZoom.limits.y2=svgPanZoom.getViewBox().height+500
                }
                
                let x=svgPanZoom.getViewBox().x;
                // svgPanZoom.setViewBox(svgPanZoom.getViewBox().x/1.45,svgPanZoom.getViewBox().y/1.45,1950,1300,100)
                svgPanZoom.setViewBox(x,svgPanZoom.getViewBox().y/1.625,1950,1300,100)
                // if(width>436) svgPanZoom.setViewBox(svgPanZoom.getViewBox().x,svgPanZoom.getViewBox().y,1950,1300,100)
                if(isUnSelectItem){
                    setTimeout(()=>svgPanZoom.setCenter(x*1.65+width,svgPanZoom.getViewBox().y,100),0)
                }
                
            }
            if(zoomScale===0.55){
            }
            if(width>=668){
                //default +60px limit width
                svgPanZoom.limits.x2=svgPanZoom.getViewBox().width+60
            }else{
                //default +60px limit width plus
                //every 50px width decrease, every 80px limit width increase
                svgPanZoom.limits.x2=svgPanZoom.getViewBox().width+60+((668-width)*80/50)
            }

            if((height*2)>=900){
                //default +70px limit height
                svgPanZoom.limits.y2=svgPanZoom.getViewBox().height+70
            }
        }else{
            svgPanZoom.zoomOut();
            if(zoomScale===1){
                svgPanZoom.limits.x2=(1200+(1200-width))+(isFirstZoomIn===true?0:-20)
                svgPanZoom.limits.y2=(800+(800-height))
            }
            if(zoomScale===1.25){
                if(width>=1000){
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-40
                    svgPanZoom.limits.y2=(800+(800-height))*times-20
                }else if(width>=800){
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-55
                    svgPanZoom.limits.y2=(800+(800-height))*times-20
                }else{
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-130
                    svgPanZoom.limits.y2=(800+(800-height))*times-20
                }
                if(height<600){
                    svgPanZoom.limits.y2=(800+(800-height))*times-30
                }
            }
            if(zoomScale===1.5){
                if(width>=1000){
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-80
                    svgPanZoom.limits.y2=(800+(800-height))*times-15
                }else if(width>=800){
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-95
                    svgPanZoom.limits.y2=(800+(800-height))*times-15
                }else{
                    svgPanZoom.limits.x2=(1200+(1200-width))*times-190
                    svgPanZoom.limits.y2=(800+(800-height))*times-15
                }
                if(height<600){
                    svgPanZoom.limits.y2=(800+(800-height))*times-70
                }
            }
        }

        //prevent over limit y when zoom in
        setTimeout(()=>{
            let svgPanZoomViewBox=svgPanZoom.getViewBox();
            if(svgPanZoomViewBox.y===0){
                svgPanZoom.panUp(0,100);
            }
        },700)
    }
}
const loadPanButton=()=>{
    let panButtonGroup=$(".modal-popup .popup-box .floor-plan-container .floor-plan .pan-button-group");
    const panUpAriaLabel=currentPageLang === 'zh-hk' ? '向上' : currentPageLang === 'zh-cn' ? '向上' : 'Up';
    const panDownAriaLabel=currentPageLang === 'zh-hk' ? '向下' : currentPageLang === 'zh-cn' ? '向下' : 'Down';
    const panLeftAriaLabel=currentPageLang === 'zh-hk' ? '向左' : currentPageLang === 'zh-cn' ? '向左' : 'Left';
    const panRightAriaLabel=currentPageLang === 'zh-hk' ? '向右' : currentPageLang === 'zh-cn' ? '向右' : 'Right';
    const panCenterAriaLabel=currentPageLang === 'zh-hk' ? '置中' : currentPageLang === 'zh-cn' ? '置中' : 'Center';
    let panButton=`<div><button class='pan-up' onclick='svgPan("up")' aria-label="${panUpAriaLabel}">&#8593;</button><button class='pan-center' onclick='svgPan("center")' aria-label="${panCenterAriaLabel}">&#8857;</button><button class='pan-left' onclick='svgPan("left")' aria-label="${panLeftAriaLabel}">&#8592;</button><button class='pan-down' onclick='svgPan("down")' aria-label="${panDownAriaLabel}">&#8595;</button><button class='pan-right' onclick='svgPan("right")' aria-label="${panRightAriaLabel}">&#8594;</button></div>`;
    panButtonGroup.html(panButton)
}
const svgPan=(direction)=>{
    if(direction==="left") return svgPanZoom.panLeft(30, 300)
    if(direction==="right") return svgPanZoom.panRight(30, 300)
    if(direction==="up") return svgPanZoom.panUp(30, 300)
    if(direction==="down") return svgPanZoom.panDown(30, 300)
    let isMobile=(window.innerWidth<=768||window.innerHeight<528)?true:false;
    let floorPlanMap=$(".modal-popup .popup-box .floor-plan-container .floor-plan .map");
    const width=floorPlanMap.width();
    const height=floorPlanMap.height();
    if(isMobile){
        if(zoomScale===1){
            zoomOutFunc()
        }
        if(zoomScale===0.55){
            zoomOutFunc()
        }
        zoomScale=0.1;
    }
    setTimeout(() => {
        if(direction==="center"){
            if(isMobile){
                let extraRightPan=40
                if(width>=430&&width<=460){
                    extraRightPan=0
                }else if(width>=460&&width<=480){
                    extraRightPan=-40
                }else if(width>=480&&width<=509){
                    extraRightPan=-80
                }else if(width>=509&&width<=529){
                    extraRightPan=-120
                }else if(width>=529&&width<=558){
                    extraRightPan=-160
                }else if(width>=558&&width<=588){
                    extraRightPan=-200
                }else if(width>=588&&width<=617){
                    extraRightPan=-240
                }else if(width>=617&&width<=647){
                    extraRightPan=-280
                }else if(width>=647&&width<=768){
                    extraRightPan=-320
                }
                return svgPanZoom.setCenter(svgPanZoom.getViewBox().width/2+width/2+extraRightPan,svgPanZoom.getViewBox().height/2+height/2,100);
            }else{
                return svgPanZoom.setCenter((1200+(1200-width))/2, (800+(800-height))/2, 0)
            }
        }
    }, (isMobile?300:0));
}
const leftFloorButtonActive=(floorInt,leftFloorButton)=>{
    $(".modal-popup .popup-box .floor-plan-container .floor-plan .left-floor-button-group>button").css("background","white");
    $(".modal-popup .popup-box .floor-plan-container .floor-plan .left-floor-button-group>button").css("color","black");
    $(".modal-popup .popup-box .floor-plan-container .floor-plan .left-floor-button-group>button").removeAttr("aria-current");
    $(leftFloorButton).attr("aria-current",true);
    leftFloorButton.style.background="#EA7119";
}
const floorplanItemTooltipTitleCountText=(text)=>{
 return `<div class='count-text' style='opacity:0;color:white;display:inline-block;font-size:1rem;font-family: "NotoSans-Regular";white-space: pre-line;line-height:16px;'>${text}</div>`;
}
const loadSvgFloorPlan=(floorInt)=>{
    let langKey="en";
    let currentLang = getLang();
    if(currentLang==="zh-hk"){
        langKey="tc";
    }else if(currentLang==="zh-cn"){
        langKey="sc";
    }
    let floorPlanMap=$(".modal-popup .popup-box .floor-plan-container .floor-plan .map");
    floorPlanMap.css("opacity",0);
    let floorPlanAssetName="desktop/floorplan-gf-desktop";
    if(floorInt===0&&(langKey==="tc"||langKey==="sc")){
            floorPlanAssetName+="-"+langKey;
    }
    let floorStr='G/F';
    if(floorInt===1){
        floorPlanAssetName="desktop/floorplan-1f-new";
        floorStr='1/F'
    }else if(floorInt===2){
        floorPlanAssetName="desktop/floorplan-2f-new";
        floorStr='2/F'
    }
    if(window.innerWidth<=768||window.innerHeight<528){
        // floorPlanAssetName="mobile/floorplan-gf-mobile";
        floorPlanAssetName="desktop/floorplan-gf-desktop";
        if(floorInt===0&&(langKey==="tc"||langKey==="sc")){
            floorPlanAssetName+="-"+langKey;
        }
        if(floorInt===1){
            // floorPlanAssetName="mobile/floorplan-1f-mobile";
            floorPlanAssetName="desktop/floorplan-1f-new";
        }else if(floorInt===2){
            // floorPlanAssetName="mobile/floorplan-2f-mobile";
            floorPlanAssetName="desktop/floorplan-2f-new";
        }
    }
    let floorPlanAssetPath=`/assets/img/svg/${floorPlanAssetName}.svg`;
    floorPlanMap.load(floorPlanAssetPath,()=>{
        $.get('/include/json/floorPlan.json?'+new Date().getTime(),(data)=>{
            floorPlanData=data;
            const floorPlanDescription=data.floorPlanList.filter(item=>item.floor===floorStr);
            const categoryList=data.categoryList
            let currentLang = getLang();
            let langKey="en";
            if(currentLang==="zh-hk"){
                langKey="tc";
            }else if(currentLang==="zh-cn"){
                langKey="sc";
            }
            //build tooltip
            $("svg>g[id^=facility-],svg>g[id^=gallery-],svg>g[id^=display-],svg>g[id$=-entrance]").each(function(index){
                let text="";
                let buttonText="";
                const floorPlanDataItem=floorPlanDescription.find((row)=>{return row.id===$(this).attr('id')});
                if(floorPlanDataItem){
                    if(floorPlanDataItem['show']===false){
                        $(this).hide();
                        return true;
                    }
                    text=floorPlanDataItem?.name?.[langKey]||'';
                    buttonText=floorPlanDataItem?.details?.[langKey]||'';
                    if(currentLang==="zh-hk"){
                        text=floorPlanDataItem?.name?.[langKey]||'';
                        buttonText=floorPlanDataItem?.details?.[langKey]||'';
                    }else if(currentLang==="zh-cn"){
                        text=floorPlanDataItem?.name?.[langKey]||'';
                        buttonText=floorPlanDataItem?.details?.[langKey]||'';
                    }
                }else{
                    return true;
                }
                let buttonHeight=buttonText.length>0?40:0;
                let buttonWidth=0;
                $(".map").append(floorplanItemTooltipTitleCountText(text));
                let textWidth = $('.count-text').width();
                let textHeight = $('.count-text').height();
                $('.count-text').remove();

                if(buttonText.length>0){
                    $(".map").append(`<div class='count-text' style='opacity:0;color:white;display:inline-block;font-size:12px;font-family: "NotoSans-Regular";white-space: pre-line;line-height:12px;'>${buttonText}</div>`);
                    buttonWidth =$('.count-text').width();
                    $('.count-text').remove();
                }
                
                const {width: gWidth,height: gHeight}=this.getBoundingClientRect();
                //add a g tag first, then add rect,text,circle,poly inside it
                var svgns = "http://www.w3.org/2000/svg";
                var gEle = document.createElementNS(svgns, 'g');
                gEle.setAttribute('id',$(this).attr('id')+'-popover')
                gEle.setAttribute("transform",$(this).attr('transform'));
                gEle.setAttribute("style","display:none;");
                const translate=$(this).attr('transform').replace("translate(","").replace(")","").split(" ");
                let yTranslate=parseFloat(translate[1])
                if(yTranslate<100){
                    gEle.setAttribute("transform","translate("+translate[0]+","+(yTranslate+140)+")");
                }
                this.appendChild(gEle);
                //rectMaxWidth for View Details button width large than name text width
                let rectMaxWidth=textWidth+32;
                if(rectMaxWidth<(buttonWidth+32)){
                    rectMaxWidth=buttonWidth+32;
                }
                let rect = document.createElementNS(svgns, 'rect');
                rect.setAttribute('x', -(rectMaxWidth)/2+gWidth/2);
                rect.setAttribute('y', -(textHeight+32+buttonHeight)+gHeight/2-30);
                if(yTranslate<100&&buttonText.length===0){
                    rect.setAttribute('y', -(textHeight+32+buttonHeight)+gHeight/2-70);
                }
                
                rect.setAttribute('width', rectMaxWidth);
                rect.setAttribute('height', textHeight+32+buttonHeight);
                rect.setAttribute('style', 'fill:rgba(0,0,0,0.7);z-index:9;');
                rect.setAttribute('class', 'rect');
                gEle.appendChild(rect);
                //text
                const textSplit=text.replaceAll("<br />","*@|*").replaceAll("\n","*@|*").split("*@|*");
                let isAutoSplitText=false;

                let maxWidth=0;
                for(let index=0; index<textSplit.length; index++){
                    let splitedText = textSplit[index];
                    $(".map").append(floorplanItemTooltipTitleCountText(splitedText));
                    let subTextWidth = $('.count-text').width()+32;
                    $('.count-text').remove();
                    if(subTextWidth>300){
                        isAutoSplitText=true;
                        let splitedTextArray=langKey==="en"?splitedText.split(" "):splitedText.split("");
                        let subTextSplit=[];
                        let leftPointer = 0, rightPointer = splitedTextArray.length - 1;
                        while (leftPointer <= rightPointer) {
                            let subText = langKey==="en"?splitedTextArray.slice(leftPointer, rightPointer + 1).join(' '):splitedTextArray.slice(leftPointer, rightPointer + 1).join('');
                            $(".map").append(floorplanItemTooltipTitleCountText(subText));
                            let subTextWidth = $('.count-text').width();
                            $('.count-text').remove();
                            if (subTextWidth >= 300) {
                                rightPointer--;
                            } else {
                                maxWidth=subTextWidth>maxWidth?subTextWidth:maxWidth;
                                subTextSplit.push(subText);
                                leftPointer = rightPointer + 1;
                                rightPointer=splitedTextArray.length - 1;
                            }
                        }
                        textSplit.splice(index,1,...subTextSplit);
                    }
                }
                if(isAutoSplitText){
                    textWidth=maxWidth;
                    textHeight=16*textSplit.length;
                    rectMaxWidth=textWidth+32;
                    rect.setAttribute('x', -(rectMaxWidth)/2+gWidth/2);
                    rect.setAttribute('width', rectMaxWidth);
                    rect.setAttribute('y', -(16*textSplit.length+32+buttonHeight)+gHeight/2-30);
                    rect.setAttribute('height', textHeight+32+buttonHeight);
                }
                
                textSplit.forEach((splitedText,index)=>{
                    $(".map").append(floorplanItemTooltipTitleCountText(splitedText));
                    let subTextWidth= $('.count-text').width();
                    $('.count-text').remove();
                    let textEle= document.createElementNS(svgns, 'text');
                    textEle.setAttribute('x',-(rectMaxWidth)/2+gWidth/2+16+((textWidth>buttonWidth?textWidth:buttonWidth)-subTextWidth)/2+(rectMaxWidth-32-(textWidth>buttonWidth?textWidth:buttonWidth)));
                    textEle.setAttribute('y', -(textHeight+32+buttonHeight)+gHeight/2+index*19);
                    if(yTranslate<100&&buttonText.length===0){
                        textEle.setAttribute('y', -(textHeight+32+buttonHeight)+gHeight/2+index*19-40);
                    }
                    textEle.setAttribute('style', 'fill:#fff;font-size:1rem;font-family:"NotoSans-Regular";user-select: none;white-space: pre-line;line-height:16px;');
                    textEle.textContent = splitedText;
                    gEle.appendChild(textEle);
                })
                //close button
                const closeButton=document.createElementNS(svgns,'g');
                closeButton.setAttribute('class','btn-close-popover');
                closeButton.setAttribute('x',-(rectMaxWidth)/2+gWidth/2+rectMaxWidth-20);
                closeButton.setAttribute('y',-(textHeight+32+buttonHeight)+gHeight/2-30);
                closeButton.setAttribute('width',20);
                closeButton.setAttribute('height',20);
                closeButton.setAttribute('style','cursor:pointer');
                closeButton.setAttribute('onclick','closeViewDetailSidebar();inactiveFloorPlanItem();');
                closeButton.setAttribute('ontouchstart','let isMobile=(window.innerWidth<=768||window.innerHeight<=528)?true:false;inactiveFloorPlanItem();if(isMobile){if(zoomScale===1){zoomOutFunc(true);}setTimeout(()=>{if(zoomScale===0.55){zoomOutFunc();}},100);setTimeout(()=>{svgPan("center");},300)}')
                closeButton.setAttribute('onkeydown','if(event.key==="Enter"){document.querySelector(".'+$(this).attr('id')+'").focus();closeViewDetailSidebar();inactiveFloorPlanItem();}')
                closeButton.setAttribute('tabindex',0)
                closeButton.setAttribute('focusable',"true")
                //add rect to help onclick larger box
                let rect1=document.createElementNS(svgns,'rect');
                rect1.setAttribute('x',-(rectMaxWidth)/2+gWidth/2+rectMaxWidth-20);
                rect1.setAttribute('y',-(textHeight+32+buttonHeight)+gHeight/2-30);
                rect1.setAttribute('width',20);
                rect1.setAttribute('height',20);
                rect1.setAttribute('style','fill:transparent;');
                closeButton.appendChild(rect1);
                //add two line to make cross icon
                let line1=document.createElementNS(svgns,'line');
                line1.setAttribute('x1',-(rectMaxWidth)/2+gWidth/2+rectMaxWidth-14);
                line1.setAttribute('y1',-(textHeight+32+buttonHeight)+gHeight/2-24);
                line1.setAttribute('x2',-(rectMaxWidth)/2+gWidth/2+rectMaxWidth-6);
                line1.setAttribute('y2',-(textHeight+32+buttonHeight)+gHeight/2-16);
                line1.setAttribute('stroke','#b5b5b5');
                line1.setAttribute('stroke-width',"1");
                closeButton.appendChild(line1);
                let line2=document.createElementNS(svgns,'line');
                line2.setAttribute('x1',-(rectMaxWidth)/2+gWidth/2+rectMaxWidth-6);
                line2.setAttribute('y1',-(textHeight+32+buttonHeight)+gHeight/2-24);
                line2.setAttribute('x2',-(rectMaxWidth)/2+gWidth/2+rectMaxWidth-14);
                line2.setAttribute('y2',-(textHeight+32+buttonHeight)+gHeight/2-16);
                line2.setAttribute('stroke','#b5b5b5');
                line2.setAttribute('stroke-width',"1");
                closeButton.appendChild(line2);
                gEle.appendChild(closeButton);
                //triangle
                let polygonEle=document.createElementNS(svgns,'polygon');
                polygonEle.setAttribute('points',`${gWidth/2-10},${gHeight/2-30.15} ${gWidth/2+10},${gHeight/2-30.15} ${gWidth/2},${gHeight/2-20.15}`)
                // rectMaxWidth
                if(yTranslate<100){
                    polygonEle.setAttribute('points',`${gWidth/2-10},${-gHeight/2-15} ${gWidth/2+10},${-gHeight/2-15} ${gWidth/2},${-gHeight/2-25}`)
                }
                polygonEle.setAttribute('style', 'fill:rgba(0,0,0,0.7);');
                gEle.appendChild(polygonEle);
                //button on tooltip (View Details)
                if(buttonText.length>0){
                    let viewDetailEventString='if(document.querySelector("#'+$(this).attr('id')+'")?.classList.contains("active")===false){simClickEvent("#'+$(this).attr('id')+'")};viewDetailsSidebar("'+$(this).attr('id')+'")'
                    //make g tag
                    let gEle2=document.createElementNS(svgns,'g');
                    gEle2.setAttribute('id',$(this).attr('id')+'-view-details');
                    gEle2.setAttribute('x', -(rectMaxWidth)/2+gWidth/2+(rectMaxWidth)/2-buttonWidth/2-8+(rectMaxWidth-32-(textWidth>buttonWidth?textWidth:buttonWidth))/2);
                    gEle2.setAttribute('y', -(textHeight+32+buttonHeight)+gHeight/2+(textSplit.length-1)*17.6+18);
                    gEle2.setAttribute('width', buttonWidth+16);
                    gEle2.setAttribute('height', buttonHeight-16);
                    gEle2.setAttribute('style', 'cursor:pointer');
                    gEle2.setAttribute('onclick',viewDetailEventString)
                    gEle2.setAttribute('ontouchstart',viewDetailEventString)
                    gEle2.setAttribute('onkeydown','if(event.key==="Enter"){'+viewDetailEventString+'}')
                    gEle2.setAttribute('tabindex',0);
                    gEle2.setAttribute("focusable", "true");
                    gEle.appendChild(gEle2);
                    let viewDetailsEle = document.createElementNS(svgns, 'rect');
                    viewDetailsEle.setAttribute('x', -(rectMaxWidth)/2+gWidth/2+(rectMaxWidth)/2-buttonWidth/2-8+(rectMaxWidth-32-(textWidth>buttonWidth?textWidth:buttonWidth))/2);
                    viewDetailsEle.setAttribute('y', -(textHeight+32+buttonHeight)+gHeight/2+(textSplit.length-1)*17.6+18);
                    viewDetailsEle.setAttribute('width', buttonWidth+16);
                    viewDetailsEle.setAttribute('height', buttonHeight-16);
                    viewDetailsEle.setAttribute('style', 'fill:white;z-index:9;');
                    viewDetailsEle.setAttribute('rx', 14);
                    viewDetailsEle.setAttribute('class', 'rect');
                    gEle2.appendChild(viewDetailsEle);
                    let viewDetailsTextEle = document.createElementNS(svgns, 'text');
                    viewDetailsTextEle.setAttribute('x', gWidth/2-buttonWidth/2+buttonWidth/2+(rectMaxWidth-32-(textWidth>buttonWidth?textWidth:buttonWidth))/2);
                    viewDetailsTextEle.setAttribute('y', -(textHeight+32+buttonHeight)+gHeight/2+(textSplit.length-1)*17.6+32);
                    viewDetailsTextEle.setAttribute('dominant-baseline', 'middle');
                    viewDetailsTextEle.setAttribute('text-anchor', 'middle');
                    viewDetailsTextEle.setAttribute('style', 'fill:black;font-size:12px;font-family:"NotoSans-Regular";user-select: none;white-space: pre-line;line-height:12px');
                    viewDetailsTextEle.textContent = buttonText;
                    gEle2.appendChild(viewDetailsTextEle);
                }
                
                $(".map>svg").append(gEle);
            })
            loadSvgPanZoom(floorInt);
            setTimeout(() => {
                floorPlanMap.css("opacity",1)
            }, 600);
            $("svg>g[id^=facility-],svg>g[id^=gallery-],svg>g[id^=display-],svg>g[id$=-entrance]").off("mouseenter mouseleave click");
            $("svg>g[id^=facility-],svg>g[id^=gallery-],svg>g[id^=display-],svg>g[id$=-entrance]").on( "mouseenter", function (event){
                let isMobile=(window.innerWidth<=768||window.innerHeight<528)?true:false;
                if(isMobile){return;}
                $(this).css('position','relative');
                if(!$(this).hasClass("active")){
                    let findEle='path:first';
                    if($(this).attr("id").includes("entrance")){
                        findEle='path';
                    }
                    $(this).find(findEle).attr("old-fill",$(this).find(findEle).attr("fill"));
                    $(this).find(findEle).attr("fill","#dedede");
                    $("#"+$(this).attr('id')+'-popover').show();
                    $("#"+$(this).attr('id')+'-popover').off("mouseleave")
                    $("#"+$(this).attr('id')+'-popover').on("mouseleave",function(){
                        if(!$(this).hasClass("active")){
                            $(this).hide();
                            $(this).removeClass("active");
                            $("#"+$(this).attr('id').replace("-popover","")).find(findEle).attr("fill",$("#"+$(this).attr('id').replace("-popover","")).find(findEle).attr("old-fill"));
                            $("#"+$(this).attr('id').replace("-popover","")).find(findEle).attr("old-fill","");
                            $(this).off("mouseleave");
                        }
                    })
                }
            }).on( "mouseleave", function (event){
                //if statement is checking mouseover form g tag move to its popup 
                if($("#"+$(this).attr('id')+'-popover:hover').length===0){
                    if(!$(this).hasClass("active")){
                        let findEle='path:first';
                        if($(this).attr("id").includes("entrance")){
                            findEle='path';
                        }
                        $(this).find(findEle).attr("fill",$(this).find(findEle).attr("old-fill"));
                        $(this).find(findEle).attr("old-fill","");
                        $("#"+$(this).attr('id')+'-popover').hide();
                        $("#"+$(this).attr('id')+'-popover').off("mouseleave");
                    }
                }
            })
//fp-icon-lift,fp-icon-lift-2,fp-icon-locker,fp-first-aid-babycare,fp-icon-AED,fp-icon-URBTIX
            //click
            let clickEleSelector=`svg>g[id^=facility-]:not([id$=-popover]),svg>g[id^=gallery-]:not([id$=-popover]),svg>g[id^=display-]:not([id$=-popover]),svg>g[id$=-entrance]:not([id$=-popover]),
                svg>g[id^=fp-icon-]:not([id$=-popover]),svg>g[id=fp-first-aid-babycare]:not([id$=-popover])`;
            $(clickEleSelector).css('cursor','pointer')
            $(clickEleSelector).on("click touchstart",function(event){
                let activeId=[]
                document.querySelectorAll("svg>g.active").forEach(function(ele){
                    activeId.push(ele.id)
                })
                if($("svg>g.active").length>0){
                    inactiveFloorPlanItem()
                }
                let floorStr='G/F';
                if(floorInt===1){
                    floorPlanAssetName="desktop/floorplan-1f-new";
                    floorStr='1/F'
                }else if(floorInt===2){
                    floorPlanAssetName="desktop/floorplan-2f-new";
                    floorStr='2/F'
                }
                let floorPlanItemCategory=(floorPlanData.floorPlanList.filter(item=>item.floor===floorStr).find(row=>row.id===$(this).attr("id"))?.category||"Facilities")?.replaceAll(" ","-")
                if(!activeId.includes($(this).attr("id"))){
                    if(["fp-icon-toilet","fp-icon-toilet-2","fp-icon-toilet-accessibility"].includes($(this).attr("id"))){
                        if(!document.querySelector(".floor-plan-menu-category-name."+floorPlanItemCategory+".active")){
                            toggleFloorPlanMenuCategory(document.querySelector(".floor-plan-menu-category-name."+floorPlanItemCategory))
                        }
                        if(document.querySelector('.floor-plan-menu-item-list-content.fp-icon-toilet-accessibility')){
                            activeFloorPlanItem(this.id,document.querySelector('.floor-plan-menu-item-list-content.fp-icon-toilet-accessibility'));
                        }else{
                            activeFloorPlanItem(this.id,document.querySelector('.floor-plan-menu-item-list-content.fp-icon-toilet'));
                        }
                        return;
                    }
                    if(["fp-icon-lift","fp-icon-lift-2"].includes($(this).attr("id"))){
                        if(!document.querySelector(".floor-plan-menu-category-name."+floorPlanItemCategory+".active")){
                            toggleFloorPlanMenuCategory(document.querySelector(".floor-plan-menu-category-name."+floorPlanItemCategory))
                        }
                        activeFloorPlanItem(this.id,document.querySelector('.floor-plan-menu-item-list-content.fp-icon-lift'));
                        return;
                    }
                    if(!document.querySelector(".floor-plan-menu-category-name."+floorPlanItemCategory+".active")){
                        toggleFloorPlanMenuCategory(document.querySelector(".floor-plan-menu-category-name."+floorPlanItemCategory))
                    }
                    activeFloorPlanItem(this.id,document.querySelector('.floor-plan-menu-item-list-content.'+$(this).attr("id")));
                    // zoomToSelectSvgItem(this);
                }
            });
            //menu
            loadFloorPlanMenu(floorInt,floorPlanDescription,categoryList);
            //switch mobile view or desktop view
            window.removeEventListener('resize', debounceLoadSvgPanZoom);
            window.addEventListener('resize', debounceLoadSvgPanZoom);

            // $('#fp-icon-toilet,#fp-icon-toilet-2,#fp-icon-toilet-accessibility').css('cursor','pointer')
            // $('#fp-icon-toilet,#fp-icon-toilet-2,#fp-icon-toilet-accessibility').on("click",function(){
                
            // });
        })
    });
}
function simClickEvent(selectorString){
    const event = new MouseEvent('click', {
        view: window,
        bubbles: true,   // Event will bubble up the DOM tree
        cancelable: true // Event can be cancelled
    });
    document.querySelector(selectorString).dispatchEvent(event);
}
function zoomToSelectSvgItem(that){
    let isMobile=(window.innerWidth<=768||window.innerHeight<528)?true:false;
    if(isMobile){
        // let gEleWidthHeight=this.getBBox()
        // let gEleTransform=this.getAttribute('transform').replace('translate(','').replace(')','').split(" ")
        // let gEleX=parseFloat(gEleTransform[0])
        // let gEleY=parseFloat(gEleTransform[1])
        // let floorPlanMap=$(".modal-popup .popup-box .floor-plan-container .floor-plan .map");
        // let width=floorPlanMap.width();
        // let height=floorPlanMap.height();
        // svgPanZoom.setCenter((1200+(1200-width))/2+gEleX-650+gEleWidthHeight.width/2,(800+(800-height))/2+gEleY-450+gEleWidthHeight.height/2, 0)
        if(zoomScale===0.1){
            zoomInFunc()
        }
        // if(zoomScale===0.55){
        //     zoomInFunc()
        // }
        
        let gEleWidthHeight=that.getBBox()
        let gEleTransform=that.getAttribute('transform').replace('translate(','').replace(')','').split(" ")
        let gEleX=parseFloat(gEleTransform[0])
        let gEleY=parseFloat(gEleTransform[1])
        let floorPlanMap=$(".modal-popup .popup-box .floor-plan-container .floor-plan .map");
        let width=floorPlanMap.width();
        let height=floorPlanMap.height();
        let widthPan=410+(width>400?-50:0)
        // svgPanZoom.setCenter((1200+(1200-width))/2+gEleX-570+gEleWidthHeight.width/2,(800+(800-height))/2+gEleY-450+gEleWidthHeight.height/2, 500)
        svgPanZoom.setCenter(gEleX+gEleWidthHeight.width/2+widthPan,gEleY+gEleWidthHeight.height/2+height/2-50, 100)
    }else{
        if(that){
            let itemY=that.transform.baseVal[0].matrix.f;
            if(itemY<200){
                let svgPanZoomViewBox=svgPanZoom.getViewBox();
                svgPanZoom.setViewBox(svgPanZoomViewBox.x, 0, svgPanZoomViewBox.width, svgPanZoomViewBox.height, 300)
            }
        }
    }
}
function viewDetailsSidebar(text){
    let currentLang = getLang();
    let detailSidebar='';
    detailSidebar+="<div class='floor-plan-detail-sidebar'>";
    detailSidebar+="<div class='sidebar-close-button' onclick='closeViewDetailSidebar()' onkeydown='if(event.key===\"Enter\")closeViewDetailSidebar()' ontouchstart='closeViewDetailSidebar()' role='button' tabindex='0'>";
    detailSidebar+="<span>";
    let closeButtonText="Close";
    if(currentLang==="zh-cn"){
        closeButtonText="关闭";
    }else if(currentLang==="zh-hk"){
        closeButtonText="關閉";
    }
    detailSidebar+=closeButtonText;
    detailSidebar+="</span>";
    detailSidebar+=`<svg xmlns="http://www.w3.org/2000/svg" width="11.314" height="11.314" viewBox="0 0 11.314 11.314">
    <g id="Group_673" data-name="Group 673" transform="translate(-541.559 -1099.282) rotate(45)">
        <line id="Line_978" data-name="Line 978" x2="15" transform="translate(1160.75 394.37)" fill="none" stroke="#000" stroke-width="1"/>
        <line id="Line_979" data-name="Line 979" x2="15" transform="translate(1168.25 386.87) rotate(90)" fill="none" stroke="#000" stroke-width="1"/>
    </g>
    </svg>
    `;
    detailSidebar+="</div>";
    
    let floorStr='G/F';
    if(floorInt===1){
        floorStr='1/F'
    }else if(floorInt===2){
        floorStr='2/F'
    }
    let floorPlanDataItem=floorPlanData.floorPlanList.find((row)=>{return row.id===text&&row.floor===floorStr});
    if(floorPlanDataItem){
        detailSidebar+="<div class='sidebar-content'>";
        let langKey="en";
        if(currentLang==="zh-hk"){
            langKey="tc";
        }else if(currentLang==="zh-cn"){
            langKey="sc";
        }
        if(floorPlanDataItem.sidebar.imagePath){
            detailSidebar+="<img class='sidebar-image' src='"+floorPlanDataItem.sidebar.imagePath+"' alt='"+floorPlanDataItem.name?.[langKey]+"'>"
        }
        detailSidebar+="<div class='sidebar-content-2'>";
        if(floorPlanDataItem.sidebar.artwork.key?.[langKey]){
            detailSidebar+="<div class='sidebar-content-key sidebar-content-artwork'>";
            detailSidebar+=floorPlanDataItem.sidebar.artwork.key?.[langKey]
            detailSidebar+="</div>";
            detailSidebar+="<div class='sidebar-content-value sidebar-content-artwork'>";
            detailSidebar+=floorPlanDataItem.sidebar.artwork.value?.[langKey]
            detailSidebar+="</div>";
        }
        
        if(floorPlanDataItem.sidebar.description.key?.[langKey]){
            detailSidebar+="<div class='sidebar-content-key sidebar-content-description'>";
            detailSidebar+=floorPlanDataItem.sidebar.description.key?.[langKey]
            detailSidebar+="</div>";
            detailSidebar+="<div class='sidebar-content-value sidebar-content-description'>";
            detailSidebar+=floorPlanDataItem.sidebar.description.value?.[langKey]
            detailSidebar+="</div>";
        }
        
        if(floorPlanDataItem.sidebar.link.key?.[langKey]){
            detailSidebar+="<div class='sidebar-content-key'>";
            detailSidebar+=floorPlanDataItem.sidebar.link.key?.[langKey]
            detailSidebar+="</div>";
            detailSidebar+="<div class='sidebar-content-value sidebar-content-link'>";
            // detailSidebar+="<a href='"+floorPlanDataItem.sidebar.link.href?.[langKey]+"' title='"+floorPlanDataItem.sidebar.link.value?.[langKey]+"' target='_blank'>";
            detailSidebar+=floorPlanDataItem.sidebar.link.value?.[langKey]
            // detailSidebar+="</a>";
            detailSidebar+="</div>";
        }
        
        detailSidebar+="</div>";
        detailSidebar+="</div>";
    }
    detailSidebar+="</div>";
    if($(".floor-plan-detail-sidebar").length>0){
        $(".floor-plan-detail-sidebar").remove();
    }
    $(".floor-plan-container").append(detailSidebar);
    setTimeout(function(){
        $(".floor-plan-detail-sidebar").css("transform","translateX(0%)")
    },0)
    $(".floor-plan-menu-category-name").attr("tabindex","-1");
    $(".floor-plan-menu-item-list-content").attr("tabindex","-1");
    $('.floor-plan-menu').attr("aria-hidden","true");
    if(window.innerHeight<528){
        $('.sidebar-close-button').focus();
        document.querySelector('.floor-plan-container').style.overflowY="hidden";
    }
}
function closeViewDetailSidebar(){
    $(".floor-plan-detail-sidebar").css("transform","translateX(100%)")
    setTimeout(() => {
        $(".floor-plan-detail-sidebar").remove();
    }, 300);
    $(".floor-plan-menu-category-name").attr("tabindex","0");
    $(".floor-plan-menu-item-list-content").attr("tabindex","0");
    $('.floor-plan-menu').attr("aria-hidden","false");
    if(window.innerHeight<528){
        document.querySelector('.floor-plan-container').style.overflowY="auto";
    }
}
// Store the debounced function outside to maintain the same reference
let debouncedLoadSvgPanZoomHandler;
let oldWindowWidth=0,oldWindowHeight=0;
function debounceLoadSvgPanZoom() {
    // Only create the debounced function once
    if (!debouncedLoadSvgPanZoomHandler) {
        debouncedLoadSvgPanZoomHandler = debounce(() => {
            //trigger mobile to desktop or desktop to mobile
            if((oldWindowWidth<=768&&window.innerWidth>768)||(oldWindowWidth>768&&window.innerWidth<=768)||oldWindowHeight>528&&window.innerHeight<=528){
                zoomScale=1
                loadFloorButton()
                loadZoomInOutButton()
                loadSvgFloorPlan(floorInt)
            }else{
                zoomScale=1
                loadZoomInOutButton()
                loadSvgPanZoom(floorInt);
            }
            oldWindowWidth=window.innerWidth;
            oldWindowHeight=window.innerHeight;
        }, 500);
    }
    
    // Execute the debounced function
    debouncedLoadSvgPanZoomHandler();
}
let floorPlanMap
function loadSvgPanZoom(floorInt){
    let isMobile=window.innerWidth<=768||window.innerHeight<528?true:false;
    floorPlanMap=$(".modal-popup .popup-box .floor-plan-container .floor-plan .map");
    if(floorPlanMap.length>0){
        let floorPlanAssetName="floorplan-gf-desktop";
        if(floorInt===1){
            floorPlanAssetName="floorplan-1f-new";
        }else if(floorInt===2){
            floorPlanAssetName="floorplan-2f-new";
        }
        if(isMobile){
            // floorPlanAssetName="floorplan-gf-mobile";
            floorPlanAssetName="floorplan-gf-desktop";
            if(floorInt===1){
                // floorPlanAssetName="floorplan-1f-mobile";
                floorPlanAssetName="floorplan-1f-new";
            }else if(floorInt===2){
                // floorPlanAssetName="floorplan-2f-mobile";
                floorPlanAssetName="floorplan-2f-new";
            }
        }
        const width=floorPlanMap.width();
        const height=floorPlanMap.height();
        svgPanZoom = $(`.modal-popup .popup-box .floor-plan-container .floor-plan .map svg#${floorPlanAssetName}`).svgPanZoom({
            zoomFactor: (isMobile?0.625:0.25),
            maxZoom: 1.5,
            events: {
                mouseWheel: true, // enables mouse wheel zooming events
                doubleClick: false, // enables double-click to zoom-in events
                drag: true, // enables drag and drop to move the SVG events
                dragCursor: "move" // cursor to use while dragging the SVG
            },
            initialViewBox:{
                x:isMobile?0:29.7,//center
                y:isMobile?0:100,//center
                width:isMobile?1200:1200,//isMobile?675:1200,
                height:isMobile?800:800,//isMobile?450:800,
            },
            limits:{
                x:0,
                y:0,
                x2:isMobile?(1200+(1200-width)):(1200+(1200-width)),//isMobile?(675+(675-width)):(1200+(1200-width)),
                y2:isMobile?(800+(800-height)):(800+(800-height))//isMobile?(450+(450-height)):(800+(800-height))
            }
        });
        if(isMobile){
            //first zoomout, after first zoomout, width=1725,height=1150
            svgPanZoom.zoomOut(100);
            // svgPanZoom.limits.x2=(1200*1.45+(1200-width))
            
            // zoomScale=0.55
            // svgPanZoom.limits.x2=1940+768-width
            // svgPanZoom.limits.x2=1200*1.45+
            
            // svgPanZoom.limits.x2=2700-width
            // svgPanZoom.limits.y2=1910-height*1.4
            // svgPanZoom.setCenter((1200+(1200-width))/2+200,(800+(800-height))/2+50);

            //first step limit for zoomScale 0.55
            setTimeout(() => {
                if(width>=668){
                    //default +230px limit width
                    svgPanZoom.limits.x2=svgPanZoom.getViewBox().width+230
                }else{
                    //default +230px limit width plus
                    //every 50px width decrease, every 70px limit width increase
                    svgPanZoom.limits.x2=svgPanZoom.getViewBox().width+230+(668-width)*70/50
                }
                if((height*2)>=900){
                    //default +150px limit height
                    svgPanZoom.limits.y2=svgPanZoom.getViewBox().height+150
                }
                // else{
                //     //after fixed map height, follow not use
                //     //default +150px limit width plus
                //     //every 100px height decrease, every 70px limit width increase
                //     svgPanZoom.limits.y2=svgPanZoom.getViewBox().height+150+(900-(height*2))*70/100
                // }
            },200);
            //second zoomout, after second zoomout, width=1950, height=1300
            setTimeout(()=>{
                svgPanZoom.zoomOut(100)
                zoomScale=0.1
            },300);
            setTimeout(() => {
                if(width>=668){
                    //default +60px limit width
                    svgPanZoom.limits.x2=svgPanZoom.getViewBox().width+60
                }else{
                    //default +60px limit width plus
                    //every 50px width decrease, every 80px limit width increase
                    svgPanZoom.limits.x2=svgPanZoom.getViewBox().width+60+((668-width)*80/50)
                }

                if((height*2)>=900){
                    //default +70px limit height
                    svgPanZoom.limits.y2=svgPanZoom.getViewBox().height+70
                }
                // else{
                        //after fixed map height, follow not use
                //     //default +70px limit width plus
                //     //every 100px height decrease, every 80px limit width increase
                //     svgPanZoom.limits.y2=svgPanZoom.getViewBox().height+70+(900-(height*2))*80/100
                // }
                // svgPanZoom.limits.x2=3850-width*3.48
                // svgPanZoom.limits.y2=2430-height*2.4
                // svgPanZoom.setCenter((1200+(1200-width))/2+250,(800+(800-height))/2+125);

                let extraRightPan=40
                if(width>=430&&width<=460){
                    extraRightPan=0
                }else if(width>=460&&width<=480){
                    extraRightPan=-40
                }else if(width>=480&&width<=509){
                    extraRightPan=-80
                }else if(width>=509&&width<=529){
                    extraRightPan=-120
                }else if(width>=529&&width<=558){
                    extraRightPan=-160
                }else if(width>=558&&width<=588){
                    extraRightPan=-200
                }else if(width>=588&&width<=617){
                    extraRightPan=-240
                }else if(width>=617&&width<=647){
                    extraRightPan=-280
                }else if(width>=647&&width<=768){
                    extraRightPan=-320
                }
                svgPanZoom.setCenter(svgPanZoom.getViewBox().width/2+width/2+extraRightPan,svgPanZoom.getViewBox().height/2+height/2,100);
            }, 500);
        }else{
            svgPanZoom.setCenter((1200+(1200-width))/2,(800+(800-height))/2);
        }
        // svgPanZoom.setCenter(isMobile?(1200+(1200-width))/2:(1200+(1200-width))/2, isMobile?(800+(800-height))/2:(800+(800-height))/2, 0)
        try{
            svgPanZoom.events.mouseWheel= false;
        }catch(e){
            console.log(e);
        }
    }
}
function loadFloorPlanMenu(floorInt,floorPlanDescription,categoryList) {
    let currentLang = getLang();
    let langKey="en";
    if(currentLang==="zh-hk"){
        langKey="tc";
    }else if(currentLang==="zh-cn"){
        langKey="sc";
    }
    let floorName="";
    if(floorInt===0){
        floorName=floorObj[langKey].find((row)=>row.value===floorInt)?.label||'';
    }else if(floorInt===1){
        floorName=floorObj[langKey].find((row)=>row.value===floorInt)?.label||'';
    }else if(floorInt===2){
        floorName=floorObj[langKey].find((row)=>row.value===floorInt)?.label||'';
    }
    const category=[]
    floorPlanDescription.filter((row)=>row.show===true).forEach((row)=>{
        if(!category.includes(row.category)){
            category.push(row.category);
        }
    })
    category.sort((a,b)=>{
        const categoryListObj = categoryList.reduce((obj,row)=>{
            obj[row.category]=row.order;
            return obj;
        },{})
        return categoryListObj[a]-categoryListObj[b];
    });
    let menuHtml = `
    <div class="floor-plan-menu-title">${floorName}</div>
    <div class="floor-plan-menu-content">
        ${category.map((row,index)=>{
            const categoryObj=categoryList.find((row2)=>{return row2.category===row})
            return `
            <div class="floor-plan-menu-category">
                <div class="floor-plan-menu-category-name ${row.replaceAll(" ","-")}" onclick="toggleFloorPlanMenuCategory(this)" onkeydown="if(event.key==='Enter'){toggleFloorPlanMenuCategory(this)}" tabIndex=0 role="button" aria-expanded="false" aria-controls="floor-plan-menu-item-list-${row.replaceAll(" ","-")}">
                    <div>${categoryObj?.name?.[langKey]||""}</div>
                    <div>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-up" viewBox="0 0 16 16">
                            <path fill-rule="evenodd" d="M8 15a.5.5 0 0 0 .5-.5V2.707l3.146 3.147a.5.5 0 0 0 .708-.708l-4-4a.5.5 0 0 0-.708 0l-4 4a.5.5 0 1 0 .708.708L7.5 2.707V14.5a.5.5 0 0 0 .5.5"/>
                        </svg>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-down" viewBox="0 0 16 16">
                            <path fill-rule="evenodd" d="M8 1a.5.5 0 0 1 .5.5v11.793l3.146-3.147a.5.5 0 0 1 .708.708l-4 4a.5.5 0 0 1-.708 0l-4-4a.5.5 0 0 1 .708-.708L7.5 13.293V1.5A.5.5 0 0 1 8 1"/>
                        </svg>
                    </div>
                </div>
                <div class="floor-plan-menu-item-list" id="floor-plan-menu-item-list-${row.replaceAll(' ','-')}" aria-hidden="true">
                    ${floorPlanDescription.filter((item)=>item.category===row).sort((a,b)=>{return a.order-b.order}).map((item,index)=>{
                        if(item.show===false){
                            return '';
                        }
                        let html= 
                        `<div class="floor-plan-menu-item-list-content ${item?.id||""}" onclick="activeFloorPlanItem('${item?.id||""}',this,true)" onkeydown="if(event.key==='Enter'){activeFloorPlanItem('${item?.id||""}',this,true)}" tabIndex=0 role="button">`
                        +(item.category==="Facilities"?`<div class="floor-plan-menu-item-content-item-icon"><img src="/assets/img/svg/icon/${item?.iconName||""}.svg"/></div>`:``)
                        +`<div class="floor-plan-menu-item-content-item-title">${item?.name?.[langKey]?.replace("<br />"," ")||""}</div>`
                        +`</div>`;
                        return html;
                    }).join('')}
                </div>
            </div>
            `
        }).join('')}
    </div>
    `;
    $('.floor-plan-menu').html(menuHtml);
}
function toggleFloorPlanMenuCategory(self){
    $(".floor-plan-popup .floor-plan-menu-item-list").slideUp();
    $(".floor-plan-popup .floor-plan-menu-category-name.active").attr("aria-expanded",false);
    $(".floor-plan-popup .floor-plan-menu-category-name").removeClass("active");
    $(".floor-plan-popup .bi-arrow-up").hide()
    $(".floor-plan-popup .bi-arrow-down").show()
    $(".floor-plan-popup .floor-plan-menu-item-list").attr('aria-hidden',true)
    const listEle=self.parentNode.querySelector(".floor-plan-menu-item-list");
    if(listEle.style.display==='none'||listEle.style.display===''){
        $(self).addClass("active");
        $(self).find(".bi-arrow-up").show();
        $(self).find(".bi-arrow-down").hide()
        $(listEle).slideDown();
        $(listEle).attr('aria-hidden',false)
        $(self).attr("aria-expanded",true);
    }else{
        $(listEle).slideUp();
        // $(self).attr("aria-expanded",false);
    }
}
function activeFloorPlanItem(id,self,isKeyBoard=false){
    //hide old active and update menu background
    inactiveFloorPlanItem()

    //show new active
    if(id.includes("fp-icon")||id==="fp-first-aid-babycare"){ //icon
        if(id==='fp-icon-toilet-accessibility'||id==="fp-icon-toilet"||id==="fp-icon-toilet-2"){
            idList=["fp-icon-toilet","fp-icon-toilet-2","fp-icon-toilet-accessibility"];
        }else if(id==='fp-icon-lift'||id==="fp-icon-lift-2"){
            idList=["fp-icon-lift","fp-icon-lift-2"];
        }else{
            idList=[id];
        }
        idList.forEach((row)=>{
            $('#'+row).addClass('active');
            if($('#'+row).find('circle:first').length>0){
                if(!$('#'+row).find('circle:first').attr("old-fill")){
                    $('#'+row).find('circle:first').attr("old-fill",$('#'+row).find('circle:first').attr("fill"));
                }
                $('#'+row).find('circle:first').attr("fill","#EA7119");
            }else{
                if(!$('#'+row).find('ellipse:first').attr("old-fill")){
                    $('#'+row).find('ellipse:first').attr("old-fill",$('#'+row).find('ellipse:first').attr("fill"));
                }
                $('#'+row).find('ellipse:first').attr("fill","#EA7119");
            }
            
            $(`#${row}>g>g:nth-of-type(2) path,#${row}>g>g:nth-of-type(2) rect,#${row}>g>g:nth-of-type(2) circle,#${row}>g>g:nth-of-type(2) ellipse`).each(function(){
                if(!$(this).attr("old-fill")){
                    $(this).attr("old-fill",$(this).attr("fill"));
                }
            });
            
            $(`#${row}>g>g:nth-of-type(2) path,#${row}>g>g:nth-of-type(2) rect,#${row}>g>g:nth-of-type(2) circle,#${row}>g>g:nth-of-type(2) ellipse`).attr("fill","#fff")
        })
    }else{
        $('#'+id).addClass('active');
        let findEle='path:first';
        if(id.includes("entrance")){
            findEle='path';
        }
        if(!$('#'+id).find(findEle).attr("old-fill")){
            $('#'+id).find(findEle).attr("old-fill",$('#'+id).find(findEle).attr("fill"));
        }
        $('#'+id).find(findEle).attr("fill","#EA7119");
    }
    $('#'+id+"-popover").addClass('active');
    $('#'+id+"-popover").show()
    if(isKeyBoard===true){
        if($('#'+id+"-popover>"+"#"+id+"-view-details").length>0){
            setTimeout(() => {
                $('#'+id+"-popover>"+"#"+id+"-view-details").focus()
            }, 300);
        }
        if(window.innerHeight<528){//if browser zoom
            document.querySelector('.floor-plan-container').scroll(0,0)
        }
    }
    zoomToSelectSvgItem(document.getElementById(id));
    //menu
    if(self){
        $(self).addClass("active");
        $(self).css("background","#EA7119")
        setTimeout(() => {
            if(window.innerHeight>527){//if not browser zoom
                self.scrollIntoView({
                    behavior: "smooth",
                    block: "nearest"
                });
            }
        }, 500);
    }
}
function inactiveFloorPlanItem(){
    $(".map>svg>g[id$=-popover].active").hide();
    $(".map>svg>g[id$=-popover].active").removeClass("active")
    if($(".map>svg>g.active").length>0){
        if($(".map>svg>g.active").attr("id").includes("fp-icon")||$(".map>svg>g.active").attr("id")=="fp-first-aid-babycare"){
            // if($(".map>svg>g.active").find('circle:first').length>0){
                $(".map>svg>g.active").find('circle:first').attr('fill',$(".map>svg>g.active").find('circle:first').attr("old-fill"))
            // }else{
                $(".map>svg>g.active").find('ellipse:first').attr('fill',$(".map>svg>g.active").find('ellipse:first').attr("old-fill"))
            // }
            $(`.map>svg>g.active>g>g:nth-of-type(2) path,.map>svg>g.active>g>g:nth-of-type(2) rect,.map>svg>g.active>g>g:nth-of-type(2) circle,.map>svg>g.active>g>g:nth-of-type(2) ellipse`).each(function(){
                $(this).attr("fill",$(this).attr("old-fill"));
            });
        }else{
            if($(".map>svg>g.active").attr("id").includes("entrance")){
                $(".map>svg>g.active").find('path').attr('fill',$(".map>svg>g.active").find('path').attr("old-fill"))
            }else{
                $(".map>svg>g.active").find('path:first').attr('fill',$(".map>svg>g.active").find('path:first').attr("old-fill"))
            }
        }
    }
    $(".map>svg>g.active").removeClass("active")
    $(".floor-plan-menu .floor-plan-menu-item-list-content.active").css("background","#EAEAEA")
    $(".floor-plan-menu .floor-plan-menu-item-list-content.active").css("color","#000")
    $(".floor-plan-menu .floor-plan-menu-item-list-content.active").removeClass("active")
    $(".floor-plan-detail-sidebar").remove();
}
const debounce = (func, wait, immediate = false) => {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        
        if (callNow) {
            func.apply(context, args);
        }
    };
};	
$(document).ready(function() {
    /*mediaelement js for audio*/
    (function($) {
        let currentLang=getLang();
        let mejs_i18n_zh_cn={
            'mejs.plural-form': 0,			
			'mejs.download-file': '下载文件',			
			'mejs.fullscreen': '全屏',			
			'mejs.play': '播放',
			'mejs.pause': '暂停',			
			'mejs.time-slider': '时间滑动棒',
			'mejs.time-help-text': '使用作/右箭头快进1秒,使用上/下箭头快进10秒。',
			'mejs.live-broadcast' : '现场直播',			
			'mejs.current': '当前时间',
			'mejs.duration': '总时长',			
			'mejs.volume-help-text': '使用上/下箭头提高或降低音量。',
			'mejs.unmute': '取消静音',
			'mejs.mute': '静音',
			'mejs.volume-slider': '音量选择键',			
			'mejs.video-player': '视频播放器',
			'mejs.audio-player': '音频播放器',			
			'mejs.captions-subtitles': '字幕/标题',
			'mejs.captions-chapters': '章',
			'mejs.none': '无',
			'mejs.afrikaans': '南非荷兰语',
			'mejs.albanian': '阿尔巴尼亚人',
			'mejs.arabic': '阿拉伯语',
			'mejs.belarusian': '白俄罗斯',
			'mejs.bulgarian': '保加利亚语',
			'mejs.catalan': '加泰罗尼亚语',
			'mejs.chinese': '中国',
			'mejs.chinese-simplified': '中文（简体）',
			'mejs.chinese-traditional': '中国（传统）',
			'mejs.croatian': '克罗地亚语',
			'mejs.czech': '捷克',
			'mejs.danish': '丹麦语',
			'mejs.dutch': '荷兰人',
			'mejs.english': '英语',
			'mejs.estonian': '爱沙尼亚语',
			'mejs.filipino': '菲律宾',
			'mejs.finnish': '芬兰语',
			'mejs.french': '法语',
			'mejs.galician': '加利西亚',
			'mejs.german': '德语',
			'mejs.greek': '希腊语',
			'mejs.haitian-creole': '海地克里奥尔人',
			'mejs.hebrew': '希伯来语',
			'mejs.hindi': '印地语',
			'mejs.hungarian': '匈牙利',
			'mejs.icelandic': '冰岛',
			'mejs.indonesian': '印尼语',
			'mejs.irish': '爱尔兰',
			'mejs.italian': '意大利语',
			'mejs.japanese': '日本',
			'mejs.korean': '韩国人',
			'mejs.latvian': '拉脱维亚人',
			'mejs.lithuanian': '立陶宛语',
			'mejs.macedonian': '马其顿',
			'mejs.malay': '马来语',
			'mejs.maltese': '马耳他',
			'mejs.norwegian': '挪威语',
			'mejs.persian': '波斯人',
			'mejs.polish': '波兰语',
			'mejs.portuguese': '葡萄牙语',
			'mejs.romanian': '罗马尼亚语',
			'mejs.russian': '俄罗斯',
			'mejs.serbian': '塞尔维亚人',
			'mejs.slovak': '斯洛伐克语',
			'mejs.slovenian': '斯洛文尼亚语',
			'mejs.spanish': '西班牙语',
			'mejs.swahili': '斯瓦希里语',
			'mejs.swedish': '瑞典语',
			'mejs.tagalog': '他加禄语',
			'mejs.thai': '泰国',
			'mejs.turkish': '土耳其语',
			'mejs.ukrainian': '乌克兰',
			'mejs.vietnamese': '越南人',
			'mejs.welsh': '威尔士',
			'mejs.yiddish': '意第绪语'
        };
        mejs.i18n["zh-cn"]={...mejs.i18n["zh-cn"],...mejs_i18n_zh_cn};
        let mejs_i18n_zh={
			'mejs.plural-form': 0,			
			'mejs.download-file': '下載檔案',			
			'mejs.fullscreen': '全螢幕',			
			'mejs.play': '播放',
			'mejs.pause': '暫停',			
			'mejs.time-slider': '時間軸',
			'mejs.time-help-text': '使用左/右箭頭快轉1秒,上/下箭頭快轉10秒。',
			'mejs.live-broadcast' : '現場直播',			
			'mejs.current': '當前時間',
			'mejs.duration': '總時長',			
			'mejs.volume-help-text': '使用上/下箭頭提高或降低音量。',
			'mejs.unmute': '取消靜音',
			'mejs.mute': '靜音',
			'mejs.volume-slider': '音量控制鍵',			
			'mejs.video-player': '影片播放器',
			'mejs.audio-player': '音樂播放器',			
			'mejs.captions-subtitles': '字幕/標題',
			'mejs.captions-chapters': '章節',
			'mejs.none': '無',
			'mejs.afrikaans': '南非荷蘭語',
			'mejs.albanian': '阿爾巴尼亞人',
			'mejs.arabic': '阿拉伯語',
			'mejs.belarusian': '白俄羅斯',
			'mejs.bulgarian': '保加利亞語',
			'mejs.catalan': '加泰羅尼亞語',
			'mejs.chinese': '中文',
			'mejs.chinese-simplified': '简体中文',
			'mejs.chinese-traditional': '正體中文',
			'mejs.croatian': '克羅地亞語',
			'mejs.czech': '捷克',
			'mejs.danish': '丹麥語',
			'mejs.dutch': '荷蘭人',
			'mejs.english': '英語',
			'mejs.estonian': '愛沙尼亞語',
			'mejs.filipino': '菲律賓',
			'mejs.finnish': '芬蘭語',
			'mejs.french': '法語',
			'mejs.galician': '加利西亞',
			'mejs.german': '德語',
			'mejs.greek': '希臘語',
			'mejs.haitian-creole': '海地克里奧爾人',
			'mejs.hebrew': '希伯來語',
			'mejs.hindi': '印地語',
			'mejs.hungarian': '匈牙利',
			'mejs.icelandic': '冰島',
			'mejs.indonesian': '印尼語',
			'mejs.irish': '愛爾蘭',
			'mejs.italian': '意大利語',
			'mejs.japanese': '日本',
			'mejs.korean': '韓國人',
			'mejs.latvian': '拉脫維亞人',
			'mejs.lithuanian': '立陶宛語',
			'mejs.macedonian': '馬其頓',
			'mejs.malay': '馬來語',
			'mejs.maltese': '馬耳他',
			'mejs.norwegian': '挪威語',
			'mejs.persian': '波斯人',
			'mejs.polish': '波蘭語',
			'mejs.portuguese': '葡萄牙語',
			'mejs.romanian': '羅馬尼亞語',
			'mejs.russian': '俄羅斯',
			'mejs.serbian': '塞爾維亞人',
			'mejs.slovak': '斯洛伐克語',
			'mejs.slovenian': '斯洛文尼亞語',
			'mejs.spanish': '西班牙語',
			'mejs.swahili': '斯瓦希里語',
			'mejs.swedish': '瑞典語',
			'mejs.tagalog': '他加祿語',
			'mejs.thai': '泰國',
			'mejs.turkish': '土耳其語',
			'mejs.ukrainian': '烏克蘭',
			'mejs.vietnamese': '越南人',
			'mejs.welsh': '威爾士',
			'mejs.yiddish': '意第緒語'
		}
        mejs.i18n["zh"]={...mejs.i18n["zh"],...mejs_i18n_zh};
        $.extend(mejs.MepDefaults, {
            fasterslowerText: 'Faster/Slower',
            moreOptionText: currentLang==="en"?"More Option":currentLang==="zh-hk"?"更多選項":"更多选项"
        });

        // Global object to track player states
        window.audioPlayers = window.audioPlayers || {};

        
            $.extend(MediaElementPlayer.prototype, {
                buildfasterslower: function(player, controls, layers, media) {
                    var t = this;
                    
                    // Initialize player in global tracking
                    if (!window.audioPlayers[t.id]) {
                        window.audioPlayers[t.id] = {
                            step: 0,
                            player: t
                        };
                    }

                    let displaySpeed =
                        $('<div class="display-playback-speed hidden">' +
                            (currentLang == "en" ? "Playback Speed: 100%" :
                                currentLang == "zh-hk" ? "播放速度: 100%" :
                                    currentLang == "zh-cn" ? "播放速度: 100%" : "Playback Speed: 100%") +
                            '</div> ')
                            .appendTo(controls);
                    // $.get('/assets/img/svg/audio-more.svg', function(svgContent) {
                    let playSpeedButton =
                        $('<div class="mejs__button-group-more-Option" id="audio_'+t.id+'">' +
                        '<button type="button" class="mejs__button-moreOption" title="' + t.options.moreOptionText + '">'+
                        `<svg id="audio_${t.id}-icon-moreOption" class="mejs__icon-moreOption" aria-hidden="true" focusable="false" data-name="Layer 2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1.86 8.51">
                            <defs>
                                <style>
                                .cls-1 {
                                    fill: #231f20;
                                }
                                </style>
                            </defs>
                            <g id="New">
                                <g>
                                <circle class="cls-1" cx=".93" cy=".93" r=".93"/>
                                <circle class="cls-1" cx=".93" cy="4.25" r=".93"/>
                                <circle class="cls-1" cx=".93" cy="7.57" r=".93"/>
                                </g>
                            </g>
                        </svg>`+
                        '</button>' +
                        '</div>') .appendTo(controls)
                        .click(function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            // Close any open audio menus from other players and reset their steps
                            document.querySelectorAll('.audio-menu').forEach(menu => {
                                if (menu.id !== 'audio_'+t.id+'_menu') {
                                    // Get player ID from menu ID and reset its step
                                    const playerId = menu.id.replace('audio_', '').replace('_menu', '');
                                    if (window.audioPlayers[playerId]) {
                                        window.audioPlayers[playerId].step = 0;
                                    }
                                    menu.remove();
                                }
                            });
                            
                            if(window.audioPlayers[t.id].step === 0){
                                //create element
                                let buttonGroup=document.createElement('div');
                                buttonGroup.id="audio_"+t.id+"_menu";
                                buttonGroup.classList.add('audio-menu');
                                // Add click outside and ESC key event listeners
                                const handleKeyDown = function(event) {
                                    if (event.key === 'Escape') {
                                        const menu = document.getElementById('audio_'+t.id+'_menu');
                                        if (menu) {
                                            window.audioPlayers[t.id].step = 1;
                                            menu.remove();
                                            window.audioPlayers[t.id].step = 0;
                                            document.removeEventListener('keydown', handleKeyDown);
                                            document.removeEventListener('click', handleClickOutside);
                                        }
                                    }
                                };

                                const handleClickOutside = function(event) {
                                    const menu = document.getElementById('audio_'+t.id+'_menu');
                                    const button = document.getElementById('audio_'+t.id);
                                    if (menu && !menu.contains(event.target) && !button.contains(event.target)) {
                                        window.audioPlayers[t.id].step = 1;
                                        menu.remove();
                                        window.audioPlayers[t.id].step = 0;
                                        document.removeEventListener('click', handleClickOutside);
                                        document.removeEventListener('keydown', handleKeyDown);
                                    }
                                };

                                setTimeout(() => {
                                    document.addEventListener('click', handleClickOutside);
                                    document.addEventListener('keydown', handleKeyDown);
                                }, 10);
                                let playSpeedText=currentLang==="en"?"Play Speed":(currentLang==="zh-hk"?"播放速度":"播放速度")
                                let button=document.createElement('button')
                                
                                let svg=document.createElement('img');
                                svg.id=`audio_${t.id}-icon-speed`;
                                svg.classList.add('mejs__icon-speed');
                                svg.src='/assets/img/svg/audio-speed.svg';
                                svg.alt=currentLang==="en"?"audio speed icon":(currentLang==="zh-hk"?"播放速度圖標":"播放速度图标");
                                svg.style.width='20px'
                                button.appendChild(svg);
                                
                                let textSpan = document.createElement('span');
                                textSpan.textContent = playSpeedText;
                                textSpan.style.marginLeft='8px'
                                button.appendChild(textSpan);
                                button.onclick=(function(e2){
                                e2.preventDefault();
                                e2.stopPropagation();
                                document.querySelector("#audio_"+t.id+"_menu").innerHTML=""

                                //back button
                                let button2=document.createElement('button')
                                let svg=document.createElement('img');
                                svg.id=`audio_${t.id}-icon-speed`;
                                svg.classList.add('mejs__icon-speed');
                                svg.src='/assets/img/svg/arrow-left.svg';
                                svg.alt=currentLang==="en"?"audio back icon":(currentLang==="zh-hk"?"返回圖標":"返回图标");
                                svg.style.width='20px'
                                button2.appendChild(svg);

                                let textSpan = document.createElement('span');
                                let optionText=currentLang==="en"?"Option":(currentLang==="zh-hk"?"選項":"选项")
                                textSpan.textContent = optionText;
                                textSpan.style.marginLeft='8px'
                                button2.appendChild(textSpan)
                                button2.onclick=((event)=>{
                                    document.querySelector("#audio_"+t.id+"_menu").remove()
                                    window.audioPlayers[t.id].step=0
                                })
                                document.querySelector("#audio_"+t.id+"_menu").append(button2)

                                //speed button array
                                let clickButtonEvent=function (event,row) {
                                    event.preventDefault();
                                    event.stopPropagation();
                                    media.pause();
                                    media.playbackRate=(["Normal","一般"].includes(row)?1:parseFloat(row))
                                    let playSpeedText=(currentLang == "en" ? "Playback Speed:" :
                                    currentLang == "zh-hk" ? "播放速度:" :
                                        currentLang == "zh-cn" ? "播放速度:" : "Playback Speed:")
                                    $('.display-playback-speed').html(playSpeedText+" "+media.playbackRate*100+"%")
                                    media.play();
                                    document.querySelector("#audio_"+t.id+"_menu").remove()
                                    window.audioPlayers[t.id].step=0
                                };
                                let normalText=currentLang==="en"?"Normal":(currentLang==="zh-hk"?"一般":"一般")
                                let playSpeedArray=["0.5","0.75","1","1.25","1.5","1.75","2"]
                                playSpeedArray.forEach((row)=>{
                                    let button2=document.createElement('button')
                                    //play speed
                                    let button2Text=row==="1"?normalText:row
                                    let span=document.createElement('span')
                                    span.textContent=button2Text
                                    span.style.paddingLeft='28px'
                                    button2.appendChild(span)
                                    
                                    if(media.playbackRate===parseFloat(row)){
                                    let tickSpan=document.createElement('span')
                                    tickSpan.style.fontSize='16px';
                                    tickSpan.style.color='blue'
                                    tickSpan.style.position='absolute'
                                    tickSpan.style.right='20px'
                                    tickSpan.innerHTML='&#10003;'
                                    button2.appendChild(tickSpan)
                                    }


                                    button2.onclick=((event)=>clickButtonEvent(event,row))
                                    document.querySelector("#audio_"+t.id+"_menu").append(button2)
                                })
                                window.audioPlayers[t.id].step=2
                                })
                                buttonGroup.append(button);
                                document.querySelector("#audio_"+t.id).append(buttonGroup);
                                window.audioPlayers[t.id].step=1
                            }else if(window.audioPlayers[t.id].step===2){
                            }
                        })
                    // })
                    media.addEventListener('play',function() {
                    }, false);

                    media.addEventListener('pause',function() {
                    }, false);
                }
            });
    })(mejs.$);

    /*MediaElement.js*/
    let currentLang=getLang(),mediaLang='en';

    if(currentLang==="zh-hk"){
        mediaLang='zh'
    }
    if(currentLang==='zh-cn'){
        mediaLang='zh-cn'
    }

    let sourcesSelector = document.querySelectorAll('select[name=sources]'),
        sourcesTotal = sourcesSelector.length;

    for (var i = 0; i < sourcesTotal; i++) {
        sourcesSelector[i].addEventListener('change', function () {

            var media = this.closest('.players').querySelector('.mejs__container').id,player = mejs.players[media];

            player.setSrc(this.value.replace('&amp;', '&'));
            player.load();
            if (!mejs.Features.isiOS && !mejs.Features.isAndroid) {
                player.play();
            }

            var renderer = document.getElementById(player.media.id + '-rendername');
            renderer.querySelector('.src').innerHTML = '<a href="' + this.value + '" target="_blank">' + this.value + '</a>';
            renderer.querySelector('.renderer').innerHTML = player.media.rendererName;
            renderer.querySelector('.error').innerHTML = '';

        });

        // These media types cannot play at all on iOS, so disabling them
        if (mejs.Features.isiOS) {
            sourcesSelector[i].querySelector('option[value^="rtmp"]').disabled = true;
            if (sourcesSelector[i].querySelector('option[value$="webm"]')) {
                sourcesSelector[i].querySelector('option[value$="webm"]').disabled = true;
            }
            if (sourcesSelector[i].querySelector('option[value$=".mpd"]')) {
                sourcesSelector[i].querySelector('option[value$=".mpd"]').disabled = true;
            }
            if (sourcesSelector[i].querySelector('option[value$=".ogg"]')) {
                sourcesSelector[i].querySelector('option[value$=".ogg"]').disabled = true;
            }
        }
    }

    mejs.i18n.language(mediaLang);

	var mediaElements = document.querySelectorAll('audio'), i, total = mediaElements.length;

	for (let i = 0; i < total; i++) {
        mediaElements[i].preload="auto"
		let player=new MediaElementPlayer(mediaElements[i], {
            features:['playpause','current','progress','duration','volume','fullscreen','fasterslower'],
			stretching: 'auto',
            hideVolumeOnTouchDevices: false,
            autoRewind: false,
			success: function (media) {
				var renderer = document.getElementById(media.id + '-rendername');

				media.addEventListener('loadedmetadata', function () {
					var src = media.originalNode.getAttribute('src').replace('&amp;', '&');
					if (src !== null && src !== undefined) {
						// renderer.querySelector('.src').innerHTML = '<a href="' + src + '" target="_blank">' + src + '</a>';
						// renderer.querySelector('.renderer').innerHTML = media.rendererName;
						// renderer.querySelector('.error').innerHTML = '';
					}
				});

				media.addEventListener('error', function (e) {
					// renderer.querySelector('.error').innerHTML = '<strong>Error</strong>: ' + e.message;
				});
			}
		});
    player.media.addEventListener('ended', function() {
        mediaElements[i].parentElement.parentElement.parentElement.querySelector(".play-pause-text").innerHTML=(currentLang==='en'?'Play':(currentLang==="zh-hk"?"播放":"播放"));
    });
	}
    let playPauseButtonArray=document.querySelectorAll('.mejs__playpause-button');
    playPauseButtonArray.forEach((item)=>{
        let playText=currentLang==='en'?'Play':(currentLang==="zh-hk"?"播放":"播放");
        let pauseText=currentLang==='en'?'Pause':(currentLang==="zh-hk"?"暫停":"暂停")
        const newSpanEle = document.createElement('span');
        newSpanEle.classList.add('play-pause-text');
        newSpanEle.textContent=playText;
        
        item.append(newSpanEle)

        item.onclick = function(){
            if(item.classList.contains('mejs__pause')){
                item.parentNode.querySelector('.play-pause-text').textContent=playText;
            }else{
                item.parentNode.querySelector('.play-pause-text').textContent=pauseText;
            }
        };
    })
    let isHoverVolumeBar=false;
    $('.mejs__container.mejs__audio').attr('tabindex',-1);
    $('.mejs__playpause-button>button').on("keyup",function(e){
        if (e.key === 'Tab') {
            $(this.parentNode).css('outline','2px solid black');
            $(this.parentNode).css('border-radius','4px');
        }
    });
    $('.mejs__volume-button>button').on("keyup",function(e){
        if (e.key === 'Tab') {
            $(this).parent().parent().find('.mejs__horizontal-volume-container').css('border','2px solid black');
            $(this).parent().parent().find('.mejs__horizontal-volume-container').css('border-radius','4px');
            $(this).parent().parent().find('.mejs__horizontal-volume-container').css('opacity', 1);
        }
    });
    $('.mejs__volume-button>button').on("focusout",function(){
        $(this).parent().parent().find('.mejs__horizontal-volume-container').css('border','none');
        $(this).parent().parent().find('.mejs__horizontal-volume-container').css('border-radius','none');
        $(this).parent().parent().find('.mejs__horizontal-volume-container').css('opacity', 0);
        $(this).parent().parent().find('.mejs__horizontal-volume-slider').hide();
        isHoverVolumeBar=false;
    });
    $('.mejs__playpause-button>button').on("focusout",function(){
        $(this.parentNode).css('outline','2px solid transparent');
        $(this.parentNode).css('border-radius','none');
        $(this).parent().parent().find('.mejs__horizontal-volume-container').css('opacity', 0);
    });
    $('.mejs__controls').append('<div class="mejs__horizontal-volume-container"></div>')
    $('.mejs__volume-button').on("mouseenter",function(){
        if(isHoverVolumeBar===false){
            $(this).parent().parent().find('.mejs__horizontal-volume-container').css('opacity', 1);
            $(this).parent().find('.mejs__horizontal-volume-slider').show();
            isHoverVolumeBar=true;
        }
    });
    $('.mejs__horizontal-volume-slider').hide();
    $('.mejs__horizontal-volume-container,.mejs__volume-button,.mejs__horizontal-volume-slider').on("mouseout",function(e){
        if(isHoverVolumeBar===true){
            if(e.relatedTarget.tagName!=='use'
                &&e.relatedTarget.tagName!=='svg'
                &&!e.relatedTarget.classList.contains('mejs__horizontal-volume-container')
                &&!e.relatedTarget.classList.contains('mejs__horizontal-volume-slider')
                &&!e.relatedTarget.classList.contains('mejs__horizontal-volume-current')
                &&!e.relatedTarget.classList.contains('mejs__horizontal-volume-total')
                &&!e.relatedTarget.parentNode.classList.contains('mejs__volume-button')
            ){
                $(this).parent().parent().find('.mejs__horizontal-volume-container').css('opacity', 0);
                $(this).parent().find('.mejs__horizontal-volume-slider').hide();
                isHoverVolumeBar=false;
            }
        }
    })
    /*end of MediaElement.js*/

    //nav
    $('nav[aria-label]').attr('aria-label', currentPageLang === 'en' ? 'breadcrumb' : currentPageLang === 'zh-hk' ? '導航' : '导航');

    //modal close button aria-label
    let closeAriaLabel= currentLang == "zh-hk" ? '關閉' : currentLang == "zh-cn" ? '关闭' : 'Close'
    setTimeout(() => {
        $('.btn-close').attr('aria-label',closeAriaLabel);
    }, 500);

    //for collection details donate border 
    let donateSection=document.querySelector(".row.section-block.donate-section");
    if(donateSection){
        donateSection.classList.add("border-b-0")
    }
})