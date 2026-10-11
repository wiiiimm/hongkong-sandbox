var jsonInterPath = "/json/property-location";
var estatePorName = '';
var estateAccessRetunrObj = {};
var estateAccessInitJson = {};
var initReady = false;

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

function initMap(latData, longData) {
	if(initReady){
		setTimeout(function(){
		console.log("load map start");
		var map;
		var markers = [];

		var draggable = true;
		var control = false;
		control = true;

		var initLocLat = latData;
		var initLocLong = longData;
		var windowJsWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;

		var first_zoom_level = 16;
		var minzoom = 10;
		var maxzoom = 20;


		if($('#map').length != 0){

			map = L.map('map', {zoomControl: false}).setView([initLocLat,initLocLong], first_zoom_level);

			var decrypted = CryptoJS.AES.decrypt(api_key, key);
			var apikey = decrypted.toString(CryptoJS.enc.Utf8);
			
			var mapLayer= L.tileLayer('https://api.hkmapservice.gov.hk/osm/xyz/basemap/WGS84/tile/{z}/{x}/{y}.png?key=' + apikey, {
			  attribution: "",
			  minZoom:minzoom,
			  maxZoom: maxzoom,
			  id: 'APIKEY'
			});

			mapLayer.addTo(map);

			if (langCode == 'en'){
				
				L.tileLayer('https://api.hkmapservice.gov.hk/osm/xyz/label-en/WGS84/tile/{z}/{x}/{y}.png?key=' + apikey, {
					minZoom:minzoom,
					maxZoom: maxzoom,
					id: 'APIKEY'
				}).addTo(map);
				
				L.control.zoom({
					zoomInTitle:'Zoom in',
					zoomOutTitle:'Zoom out',
				}).addTo(map);
				
				/* Add attribution Start */
				var attrOptions = {
					position: 'bottomright',
					prefix: "<table role='presentation' border='0'><tr><td style='padding:0px!important;border: 0px!important;text-align: right;'><div id='gm-mapviewer-powered-by'>Powered by GeoInfo Map</div><br/><div id='copyrightDiv' style='margin:0px!important'>&copy;&nbsp;The Government of the Hong Kong SAR</div></td><td style='background:transparent;border:0px;padding: 5px;'></td><td style='padding:0px!important;border: 0px!important;'><img src='/images/LandsD.png' style=' width: 27px; left: 8px; bottom: 8px; z-index: 700;' alt='Lands Department - The Government of the Hong Kong Special Administrative Region'/></td></tr></table>"
				};
				/* Add attribution End */	

			} 
			else if (langCode == 'zh-Hans'){
					
					
				L.tileLayer('https://api.hkmapservice.gov.hk/osm/xyz/label-sc/WGS84/tile/{z}/{x}/{y}.png?key=' + apikey, {
					minZoom:minzoom,
					maxZoom: maxzoom,
					id: 'APIKEY'
				}).addTo(map);
				
				L.control.zoom({
					zoomInTitle:'放大',
					zoomOutTitle:'缩小',
				}).addTo(map);			
				
				/* Add attribution Start */
				var attrOptions = {
					position: 'bottomright',
					prefix: "<table role='presentation' border='0'><tr><td style='padding:0px!important;border: 0px!important;text-align: right;'><div id='gm-mapviewer-powered-by'>技术支援由地理资讯地图提供</div><br/><div id='copyrightDiv' style='margin:0px!important'>&copy;&nbsp;地图版权属香港特别行政区政府</div></td><td style='background:transparent;border:0px;padding: 5px;'></td><td style='padding:0px!important;border: 0px!important;'><img src='/images/LandsD.png' style=' width: 27px; left: 8px; bottom: 8px; z-index: 700;' alt='香港特别行政区政府 - 地政总署'/></td></tr></table>"
				};
				/* Add attribution End */	
				
			} 
			else if (langCode == 'zh-Hant'){
				
				
				L.tileLayer('https://api.hkmapservice.gov.hk/osm/xyz/label-tc/WGS84/tile/{z}/{x}/{y}.png?key=' + apikey, {
					minZoom:minzoom,
					maxZoom: maxzoom,
					id: 'APIKEY'
				}).addTo(map);
				
				L.control.zoom({
					zoomInTitle:'放大',
					zoomOutTitle:'縮小',
				}).addTo(map);
				
				/* Add attribution Start */
				var attrOptions = {
					position: 'bottomright',
					prefix: "<table role='presentation' border='0'><tr><td style='padding:0px!important;border: 0px!important;text-align: right;'><div id='gm-mapviewer-powered-by'>技術支援由地理資訊地圖提供</div><br/><div id='copyrightDiv' style='margin:0px!important'>&copy;&nbsp;地圖版權屬香港特別行政區政府</div></td><td style='background:transparent;border:0px;padding: 5px;'></td><td style='padding:0px!important;border: 0px!important;'><img src='/images/LandsD.png' style=' width: 27px; left: 8px; bottom: 8px; z-index: 700;' alt='香港特別行政區政府 - 地政總署'/></td></tr></table>"
				};
				/* Add attribution End */	
			}
		
		// Creating an attribution
		var attr = L.control.attribution(attrOptions);
		attr.addTo(map);
		
		L.control.pan().addTo(map);
		
		L.control.scale({ position: 'bottomright', imperial:false}).addTo(map);
		
			map.scrollWheelZoom.disable();
		}

	  	var haIcon = L.icon({
		iconUrl: '/images/location-icon.png',
		iconAnchor:  [32, 55],
		popupAnchor: [0, -35],
		iconSize: 	 [60, 60],
		});

		console.log(initLocLat);
		console.log(initLocLong);
		L.marker([initLocLat,initLocLong], {icon: haIcon, keyboard: false, alt: getTxtByLang(['Location marker', '位置標記', '位置标记'])}).addTo(map);
		console.log("load map finish");
		},1000);
	}
}

//write html
function loadInitEsateFun(obj, propId, distId){
	console.log(obj);
    $(".estate_locator_topbar--search").remove();
    $(".block_estate_locator--search-result").remove();
    $(".estate_locator_topbar").show();
    $(".estate_locator_fullwidth .block_estate_locator--search-result").remove();
    $(".btn_quick_links_mobile_container").css("left", "0px");
    $(".estate_locator_fullwidth .main_section_right").show();
    $(".estate_locator_fullwidth .main_section_left").show();
    $(".estate_locator_fullwidth .main_section_left .estate_locator_detail_row:not('.item-notes')").remove();
    var estateObj = obj;
	loadLastRevisionDate(estateObj);
	// set google map location param
    var estateLocLat = estateObj["latitude"];
    var estateLocLong = estateObj["longitude"];
    var estateName = estateObj['name'][langCode];
    var estateDist = estateObj['district'][langCode];
    var estateReg = estateObj['regionName'][langCode];
	console.log(estateName+", "+estateDist+", "+estateReg);
    var estateFullName = estateName+", "+estateDist+", "+estateReg;
    $(".main_section_right .desktop_useful_links .useful_links_content .set_useful .set_useful_a:nth-last-child(2)").attr({"data-dist":distId});
    $(".btn_quick_links_mobile_container .mobile_useful_link .set_useful .set_useful_a:nth-last-child(2)").attr({"data-dist":distId});
    $(".estate-locator-section .main_section_left .estate_locator_topbar .estate_locator_search_result").html(estateFullName);
    var output = '';
    var objCount = 1;
	var infoKey = null;
	// show plans estate id	
	var showPlans = [1321347387478,1321347387571,1321347387615,1321347387461,1321347387457,1321347387462,1321347387459,1321347387463,1321347387529,1321348400391,1321347387540,1321347387516,1321347387614,1321347387545,1321347387507,1321347387476,1321347387612,1321347387467,1321347387468,1321347387497,1321347387535,1321347387515,1321347387599,1321347387437,1321347387547,1321347387588,1321347387508,1321348400454,1321347387506,1321347387585,1321347387625,1321347387575,1321347387617,1321347387576,1321347387574,1321347387577,1321347387624,1321347387573,1321347387607,1321347387621,1321347387530,1321347387608,1321347387479,1321347387498,1321347387626,1321347387592,1321347387542,1321347387544,1321347387450,1321347387543,1321347387451,1321347387620,1321347387531,1321347387473,1321347387509,1321347387486,1321347387532,1321347387480,1321347387517,1321347387590,1321347387610,1321347387601,1321347387602,1321347387586,1321347387495,1321347387438,1321347387464,1321347387465,1321347387537,1321347387603,1321347387579,1321347387460,1321347387533,1321347387609,1321347387546,1321347387518,1321347387499,1321347387488,1321347387538,1321347387605,1321347387481,1321347387539,1321347387520,1321347387503,1321347387504,1321347387439,1321347387489,1321347387613,1321347387557,1321347387578,1321347387627,1321347387622,1321347387556,1321347387536,1321347387631,1321347387558,1321347387559,1321347387560,1321347387561,1321347387562,1321347387496,1321347387534,1321347387491,1321347387446,1321347387528,1321347387447,1321347387477,1321347387448,1321347387555,1321347387471,1321347387449,1321347387493,1321347387510,1321347387629,1321347387583,1321347387584,1321347387604,1321347387600,1321347387551,1321347387554,1321347387527,1321347387550,1321347387606,1321347387475,1321347387623,1321347387511,1321347387513,1321347387595,1321347387494,1321347387628,1321347387502,1321347387505,1321347387474,1321347387598,1321347387630,1321347387587,1321347387469,1321347387512,1321347387581,1321347387436,1321347387458,1321347387548,1321347387521,1321347387456,1321347387526,1321347387594,1321347387611,1321347387440,1321347387514,1321348400448,1321347387541,1321347387563,1321347387519,1321347387487,1321347387443,1321347387522,1321347387500,1321347387445,1321347387591,1321347387455,1321347387564,1321347387616,1321347387453,1321347387452,1321347387442,1321347387593,1321347387565,1321347387466,1321347387501,1321347387553,1321347387589,1321347387525,1321347387444,1321347387619,1321347387549,1321347387596,1321347387566,1321347387567,1321347387552,1321347387524,1321347387441,1321347387568,1321347387582,1321347387580,1321347387454,1321347387618,1321347387523,1321347387490,1321347387472,1321347387482,1321347387492,1321347387470,1321347387483,1321347387569,1321347387597,1321347387484,1321347387485,1321347387572,1321347387570,1321348400441,1321348400444,1321348400512,1321348400516,1321348400394,1321348400387,1321348400490,1321348400398,1321348400377,1321348400547,1321348400436,1321348400425,1321348400476,1321348400504,1321348400472,1321348400414,1321348400458,1321348400352,1321348400513,1321348400460,1321348400399,1321348400455,1321348400402,1321348400348,1321348400468,1321348400365,1321348400390,1321348400492,1321348400420,1321348400514,1321348400471,1321348400431,1321348400493,1321348400368,1321348400400,1321348400510,1321348400366,1321348400392,1321348400484,1414739644327,1509013438313,1509013164426,1509011366415,1510816915912,1509012112827,1509012543851,1583304100788,1536028118749,1536026890620,1599034691969,1597887423517,1543912512128,1602483620701,1604893589983,1605685110533,1565664639140,1579166844012,1605080242076,1574935434162,1624431035373,1639704214461,1663575178817,1621303838727,1673429143158,1684749611533,1692692404895,1692691955606,1692849189199,1709007258109,1722243363708,1730257724584,1736231965714,1736748649304,1737444443584,1745325437108,1754559553286,1755684960025,1755685968000,1755505973541,1755847632391,1764742292329,1764744234914,1779241670867,1782966092662,1780545421543,1783063876084,1776047940251];
	switch(parseInt(propId)) {
		case 1:
		/*
		infoKey = {
			"estateType":{"en":"Type of Estate:","zh-Hant":"屋邨類別：","zh-Hans":"屋邨类别："},"intakeYear":{"en":"Year of Intake:","zh-Hant":"入伙年份：","zh-Hans":"入伙年份："},"blockType":{"en":"Type(s) of Block(s):","zh-Hant":"樓宇類型：","zh-Hans":"楼宇类型："},"blockNo":{"en":"No. of Blocks:","zh-Hant":"樓宇座數：","zh-Hans":"楼宇座数："},"blockName":{"en":"Name of Block(s):","zh-Hant":"樓宇名稱：","zh-Hans":"楼宇名称："},"flatNo":{"en":"No. of Rental Flats:","zh-Hant":"租住單位數目#：","zh-Hans":"租住单位数目#："},"flatSize":{"en":"Flat Size (m<sup>2</sup>):","zh-Hant":"單位面積 (平方米)：","zh-Hans":"单位面积 (平方米)："},"household":{"en":"No. of Households:","zh-Hant":"住戶數目#：","zh-Hans":"住户数目#："},"population":{"en":"Authorised Population:","zh-Hant":"認可人口#：","zh-Hans":"认可人口#："},"advComm":{"en":"Estate Management Advisory Committee (EMAC):","zh-Hant":"屋邨管理諮詢委員會：","zh-Hans":"屋邨管理谘询委员会："},"officeDetail":{"en":"District Tenancy Management Office/Estate Office:","zh-Hant":"分區租約事務管理辦事處 / 屋邨辦事處：","zh-Hans":"分区租约事务管理办事处 / 屋邨办事处："},"managementDetail":{"en":"Property Management:","zh-Hant":"屋邨物業管理：","zh-Hans":"屋邨物业管理："},"carparkDetail":{"en":"Carpark Management:","zh-Hant":"停車場管理：","zh-Hans":"停车场管理："},"website":{"en":"Estate Website:","zh-Hant":"屋邨網站：","zh-Hans":"屋邨网站："},"furtherInfo":{"en":"Further Information:","zh-Hant":"更多資料：","zh-Hans":"更多资料："}
		}
		*/
		infoKey = {
			"estateType":{"en":"Type of Estate:","zh-Hant":"屋邨類別：","zh-Hans":"屋邨类别："},"intakeYear":{"en":"Year of Intake:","zh-Hant":"入伙年份：","zh-Hans":"入伙年份："},"blockType":{"en":"Type(s) of Block(s):","zh-Hant":"樓宇類型：","zh-Hans":"楼宇类型："},"blockNo":{"en":"No. of Blocks:","zh-Hant":"樓宇座數：","zh-Hans":"楼宇座数："},"blockName":{"en":"Name of Block(s):","zh-Hant":"樓宇名稱：","zh-Hans":"楼宇名称："},"flatNo":{"en":"No. of Rental Flats#:","zh-Hant":"租住單位數目#：","zh-Hans":"租住单位数目#："},"flatSize":{"en":"Flat Size (m<sup>2</sup>):","zh-Hant":"單位面積 (平方米)：","zh-Hans":"单位面积 (平方米)："},"household":{"en":"No. of Households#:","zh-Hant":"住戶數目#：","zh-Hans":"住户数目#："},"population":{"en":"Authorised Population#:","zh-Hant":"認可人口#：","zh-Hans":"认可人口#："},"officeDetail":{"en":"District Tenancy Management Office/Estate Office:","zh-Hant":"分區租約事務管理辦事處 / 屋邨辦事處：","zh-Hans":"分区租约事务管理办事处 / 屋邨办事处："},"managementDetail":{"en":"Property Management:","zh-Hant":"屋邨物業管理：","zh-Hans":"屋邨物业管理："},"carparkDetail":{"en":"Carpark Management:","zh-Hant":"停車場管理：","zh-Hans":"停车场管理："},"website":{"en":"Estate Website:","zh-Hant":"屋邨網站：","zh-Hans":"屋邨网站："},"furtherInfo":{"en":"Further Information:","zh-Hant":"更多資料：","zh-Hans":"更多资料："}
		}
		for(var key in infoKey){
			// first row
			if(objCount == 1){
				output += '<div class="estate_locator_detail_row _1">';
			}else{
				output += '<div class="estate_locator_detail_row">';
			}
			output += '<div class="estate_locator_detail_column_1"><div class="item__text">'+infoKey[key][langCode]+'</div></div>';
			if(key == "blockName"){
				var estateNameBlockArr = estateObj[key][langCode].split("<br>");
				output += '<div class="estate_locator_detail_column_2 blocks_name">';
				$.each(estateNameBlockArr, function(index) {
					output += '<div class="estate_locator_detail_block_name"><div class="item__text">'+estateNameBlockArr[index]+'<br></div></div>';
				});
				output += '</div>';
			}else{
				if((key != "blockNo") && (key != "website")){
					if (estateObj[key][langCode] != null){
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">'+estateObj[key][langCode]+'</div></div>';
					} else {
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">-</div></div>';
					}
				} else {
					if (estateObj[key] != null){
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">'+estateObj[key]+'</div></div>';
					} else {
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">-</div></div>';
					}
				}
			}
			output += '</div>';
		}
		// add to last row if prop 1
		if(langCode == 'en'){
			output += '<div class="estate_locator_detail_row">';
			output += '<div><div class="item__text">#Rounded to the nearest hundred</div></div>';
			output += '</div>';
		} else if(langCode == 'zh-Hant'){
			output += '<div class="estate_locator_detail_row">';
			output += '<div><div class="item__text">#計至最近的百位整數</div></div>';
			output += '</div>';
		} else if(langCode == 'zh-Hans'){
			output += '<div class="estate_locator_detail_row">';
			output += '<div><div class="item__text">#计至最近的百位整数</div></div>';
			output += '</div>';
		}

		// quick link
		var transactionId = parseInt(estateObj["aplySysId"]);
		if(parseInt(estateObj["aplySysId"]) == 1321348400448){ //2784
			transactionId = 1321347387541; //3122
		}
		if(parseInt(estateObj["aplySysId"]) == 1321348400454){ //2706
			transactionId = 1321347387506; //3030
		}
		if(parseInt(estateObj["aplySysId"]) == 1321348400391){//2773
			transactionId = 1321347387540; //3105
		}

		if(estateObj["secondaryMarket"] > 0 || parseInt(estateObj["aplySysId"]) == 1321348400448 || parseInt(estateObj["aplySysId"]) == 1321348400454 || parseInt(estateObj["aplySysId"]) == 1321348400391){
			var hosPath = "/" + getShortLang() + "/home-ownership/hos-secondary-market/transaction-records/transaction-records-search-detail-by-district.html?catId=2&para0=" + distId + "&para1="+ transactionId;
			$(".main_section_right .desktop_useful_links .useful_links_content .set_useful_title").after('<a href="#" onclick="PopupCenter(\''+hosPath+'\',\'title\',900,900,\'\')" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['HOS Secondary Market transaction records', '居屋第二市場成交記錄', '居屋第二市场成交记录'])+'</div></a>');
			$(".btn_quick_links_mobile_container .mobile_useful_link .set_useful_title").after('<a href="#" onclick="PopupCenter(\''+hosPath+'\',\'title\',900,900,\'\')" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['HOS Secondary Market transaction records', '居屋第二市場成交記錄', '居屋第二市场成交记录'])+'</div></a>');
		}

		if(estateObj['estateTypeCode'] != 4){
			var tPlanPath = "/"+getShortLang()+"/global-elements/estate-locator/standard-block-typical-floor-plans/index.html";

			$(".main_section_right .desktop_useful_links .useful_links_content .set_useful_title").after('<a href="#" onclick="PopupCenter(\''+tPlanPath+'\',\'title\',900,900,\'\')" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['Typical floor plans', '樓宇樣本平面圖', '楼宇样本平面图'])+'</div></a>');
			$(".btn_quick_links_mobile_container .mobile_useful_link .set_useful_title").after('<a href="#" onclick="PopupCenter(\''+tPlanPath+'\',\'title\',900,900,\'\')" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['Typical floor plans', '樓宇樣本平面圖', '楼宇样本平面图'])+'</div></a>');
		}



		if (showPlans.indexOf(parseInt(estateObj["aplySysId"]))> -1) {
			var planPath = "/" + getShortLang() + "/hostps_floorplan.html?language=" + getShortLang() + "&id=" + parseInt(estateObj["aplySysId"]);

			$(".main_section_right .desktop_useful_links .useful_links_content .set_useful_title").after('<a href="#" onclick="PopupCenter(\''+planPath+'\',\'title\',900,900,\'\')" target="_blank" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['Plans', '圖則', '图则'])+'</div></a>');
			$(".btn_quick_links_mobile_container .mobile_useful_link .set_useful_title").after('<a href="#" onclick="PopupCenter(\''+planPath+'\',\'title\',900,900,\'\')" target="_blank" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['Plans', '圖則', '图则'])+'</div></a>');
		}

		break;
		case 2:
		infoKey = {
			"soldPhase":{"en":"Sold Under:","zh-Hant":"出售期數：","zh-Hans":"出售期数："},"intakeYear":{"en":"Year of Completion:","zh-Hant":"落成年份：","zh-Hans":"落成年份："},"blockType":{"en":"Type(s) of Block(s):","zh-Hant":"樓宇類型：","zh-Hans":"楼宇类型："},"blockNo":{"en":"No. of Blocks:","zh-Hant":"樓宇座數：","zh-Hans":"楼宇座数："},"blockName":{"en":"Name of Block(s):","zh-Hant":"樓宇名稱：","zh-Hans":"楼宇名称："},"flatNo":{"en":"No. of Flats:","zh-Hant":"單位數目：","zh-Hans":"单位数目："},"grossFloorArea":{"en":"Gross Floor Area of Flat (m<sup>2</sup>):","zh-Hant":"單位建築面積 (平方米)：","zh-Hans":"单位建筑面积 (平方米)："},"saleableArea":{"en":"Saleable Area of Flats (m<sup>2</sup>):","zh-Hant":"單位實用面積 (平方米)：","zh-Hans":"单位实用面积 (平方米)："},"salePrice":{"en":"Initial Sale Price($):","zh-Hant":"首次推出售價 ($)：","zh-Hans":"首次推出售价 ($)："},"ownerCorp":{"en":"Owners' Corporation:","zh-Hant":"業主立案法團：","zh-Hans":"业主立案法团："},"officeDetail":{"en":"Regional Management Office / Management Office / Estate Office:","zh-Hant":"區域物業管理辦事處 / 分區租約事務：","zh-Hans":"区域物业管理办事处 / 分区租约事务："},"managementDetail":{"en":"Property Management:","zh-Hant":"屋苑物業管理：","zh-Hans":"屋苑物业管理："},"carparkDetail":{"en":"Carpark Management:","zh-Hant":"停車場管理：","zh-Hans":"停车场管理："},"website":{"en":"Court Website:","zh-Hant":"屋苑網站：","zh-Hans":"屋苑网站："},"furtherInfo":{"en":"Further Information:","zh-Hant":"更多資料：","zh-Hans":"更多资料："}
		}
		for(var key in infoKey){
			// first row
			if(objCount == 1){
				output += '<div class="estate_locator_detail_row _1">';
			}else{
				output += '<div class="estate_locator_detail_row">';
			}
			output += '<div class="estate_locator_detail_column_1"><div class="item__text">'+infoKey[key][langCode]+'</div></div>';
			if(key == "blockName"){
				var estateNameBlockArr = estateObj[key][langCode].split("<br>");
				output += '<div class="estate_locator_detail_column_2 blocks_name">';
				$.each(estateNameBlockArr, function(index) {
					output += '<div class="estate_locator_detail_block_name"><div class="item__text">'+estateNameBlockArr[index]+'<br></div></div>';
				});
				output += '</div>';
			}else{
				if((key != "blockNo") && (key != "website") && (key != "grossFloorArea") && (key != "saleableArea") && (key != "salePrice")){
					if (estateObj[key][langCode] != null){
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">'+estateObj[key][langCode]+'</div></div>';
					} else {
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">-</div></div>';
					}
				} else {
					if (estateObj[key] != null){
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">'+estateObj[key]+'</div></div>';
					} else {
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">-</div></div>';
					}
				}
			}
			output += '</div>';
		}

		// quick link
		var transactionId = parseInt(estateObj["aplySysId"]);
		if(parseInt(estateObj["aplySysId"]) == 1321348400448){ //2784
			transactionId = 1321347387541;// 3122
		}
		if(parseInt(estateObj["aplySysId"]) == 1321348400454){//2706
			transactionId = 1321347387506; //3030
		}
		if(parseInt(estateObj["aplySysId"]) == 1321348400391){//2773
			transactionId = 1321347387540; //3105
		}

		if(estateObj["secondaryMarket"] > 0 || parseInt(estateObj["aplySysId"]) == 1321348400448 || parseInt(estateObj["aplySysId"]) == 1321348400454 || parseInt(estateObj["aplySysId"]) == 1321348400391){
			var hosPath = "/" + getShortLang() + "/home-ownership/hos-secondary-market/transaction-records/transaction-records-search-detail-by-district.html?catId=2&para0=" + distId + "&para1="+ transactionId;
			$(".main_section_right .desktop_useful_links .useful_links_content .set_useful_title").after('<a href="#" onclick="PopupCenter(\''+hosPath+'\',\'title\',900,900,\'\')" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['HOS Secondary Market transaction records', '居屋第二市場成交記錄', '居屋第二市场成交记录'])+'</div></a>');
			$(".btn_quick_links_mobile_container .mobile_useful_link .set_useful_title").after('<a href="#" onclick="PopupCenter(\''+hosPath+'\',\'title\',900,900,\'\')" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['HOS Secondary Market transaction records', '居屋第二市場成交記錄', '居屋第二市场成交记录'])+'</div></a>');
		}

		if (showPlans.indexOf(parseInt(estateObj["aplySysId"]))> -1) {
			var planPath = "/" + getShortLang() + "/hostps_floorplan.html?language=" + getShortLang() + "&id=" + parseInt(estateObj["aplySysId"]);

			$(".main_section_right .desktop_useful_links .useful_links_content .set_useful_title").after('<a href="#" onclick="PopupCenter(\''+planPath+'\',\'title\',900,900,\'\')" target="_blank" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['Plans', '圖則', '图则'])+'</div></a>');
			$(".btn_quick_links_mobile_container .mobile_useful_link .set_useful_title").after('<a href="#" onclick="PopupCenter(\''+planPath+'\',\'title\',900,900,\'\')" target="_blank" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['Plans', '圖則', '图则'])+'</div></a>');
		}

		break;
		case 3:
		infoKey = {
			"intakeYear":{"en":"Year of Completion:","zh-Hant":"落成年份：","zh-Hans":"落成年份："},"floorNo":{"en":"No. of Floor(s):","zh-Hant":"層數：","zh-Hans":"层数："},"lettableArea":{"en":"Total Lettable Area (m<sup>2</sup>):","zh-Hant":"可出租面積 (平方米)：","zh-Hans":"可出租面积 (平方米)："},"managementDetail":{"en":"Property Management:","zh-Hant":"物業管理：","zh-Hans":"物业管理："},"carparkDetail":{"en":"Carpark Management:","zh-Hant":"停車場管理：","zh-Hans":"停车场管理："},"website":{"en":"Shopping Centre Website:","zh-Hant":"商場網站：","zh-Hans":"商场网站："},"furtherInfo":{"en":"Further Information:","zh-Hant":"更多資料：","zh-Hans":"更多资料："}
		}
		for(var key in infoKey){
			// first row
			if(objCount == 1){
				output += '<div class="estate_locator_detail_row _1">';
			}else{
				output += '<div class="estate_locator_detail_row">';
			}
			output += '<div class="estate_locator_detail_column_1"><div class="item__text">'+infoKey[key][langCode]+'</div></div>';
			if(key == "blockName"){
				var estateNameBlockArr = estateObj[key][langCode].split("<br>");
				output += '<div class="estate_locator_detail_column_2 blocks_name">';
				$.each(estateNameBlockArr, function(index) {
					output += '<div class="estate_locator_detail_block_name"><div class="item__text">'+estateNameBlockArr[index]+'<br></div></div>';
				});
				output += '</div>';
			}else{
				if((key != "website")){
					if (estateObj[key][langCode] != null){
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">'+estateObj[key][langCode]+'</div></div>';
					} else {
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">-</div></div>';
					}
				} else {
					if (estateObj[key] != null){
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">'+estateObj[key]+'</div></div>';
					} else {
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">-</div></div>';
					}
				}
			}
			output += '</div>';
		}
		break;
		case 4:
		infoKey = {
			"estateType":{"en":"Type of Estate:","zh-Hant":"屋邨類別：","zh-Hans":"屋邨类别："},"intakeYear":{"en":"Year of Completion:","zh-Hant":"落成年份：","zh-Hans":"落成年份："},"blockNo":{"en":"No. of Blocks:","zh-Hant":"樓宇座數：","zh-Hans":"楼宇座数："},"blockName":{"en":"Name of Block(s):","zh-Hant":"樓宇名稱：","zh-Hans":"楼宇名称："},"flatNo":{"en":"No. of Units:","zh-Hant":"單位數目：","zh-Hans":"单位数目："},"storey":{"en":"Storey:","zh-Hant":"層數：","zh-Hans":"层数："},"officeDetail":{"en":"Factory Estate Office:","zh-Hant":"工廠大廈辦事處：","zh-Hans":"工厂大厦办事处："},"managementDetail":{"en":"Property Management:","zh-Hant":"物業管理：","zh-Hans":"物业管理："},"carparkDetail":{"en":"Carpark Management:","zh-Hant":"停車場管理：","zh-Hans":"停车场管理："},"website":{"en":"Flatted Factories Website:","zh-Hant":"工廠大廈網站：","zh-Hans":"工厂大厦网站："},"furtherInfo":{"en":"Further Information:","zh-Hant":"更多資料：","zh-Hans":"更多资料："}
		}
		for(var key in infoKey){
			// first row
			if(objCount == 1){
				output += '<div class="estate_locator_detail_row _1">';
			}else{
				output += '<div class="estate_locator_detail_row">';
			}
			output += '<div class="estate_locator_detail_column_1"><div class="item__text">'+infoKey[key][langCode]+'</div></div>';
			if(key == "blockName"){
				var estateNameBlockArr = estateObj[key][langCode].split("<br>");
				output += '<div class="estate_locator_detail_column_2 blocks_name">';
				$.each(estateNameBlockArr, function(index) {
					output += '<div class="estate_locator_detail_block_name"><div class="item__text">'+estateNameBlockArr[index]+'<br></div></div>';
				});
				output += '</div>';
			}else{
				if((key != "website")){
					if (estateObj[key][langCode] != null){
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">'+estateObj[key][langCode]+'</div></div>';
					} else {
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">-</div></div>';
					}
				} else {
					if (estateObj[key] != null){
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">'+estateObj[key]+'</div></div>';
					} else {
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">-</div></div>';
					}
				}
			}
			output += '</div>';
		}
		break;
		case 5:
		infoKey = {
			"intakeYear":{"en":"Year of Completion:","zh-Hant":"落成年份：","zh-Hans":"落成年份："},"floorNo":{"en":"No. of Floor(s):","zh-Hant":"樓層：","zh-Hans":"层数："},"lettableArea":{"en":"Total Lettable Area (m<sup>2</sup>):","zh-Hant":"可出租面積 (平方米)：","zh-Hans":"可出租面积 (平方米)："},"managementDetail":{"en":"Property Management:","zh-Hant":"物業管理：","zh-Hans":"物业管理："},"carparkDetail":{"en":"Carpark Management:","zh-Hant":"停車場管理：","zh-Hans":"停车场管理："},"website":{"en":"Commercial Premise to Lease Website:","zh-Hant":"商業場所租賃網站：","zh-Hans":"商业场所租赁网站："},"furtherInfo":{"en":"Further Information:","zh-Hant":"更多資料：","zh-Hans":"更多资料："}
		}
		for(var key in infoKey){
			// first row
			if(objCount == 1){
				output += '<div class="estate_locator_detail_row _1">';
			}else{
				output += '<div class="estate_locator_detail_row">';
			}
			output += '<div class="estate_locator_detail_column_1"><div class="item__text">'+infoKey[key][langCode]+'</div></div>';
			if(key == "blockName"){
				var estateNameBlockArr = estateObj[key][langCode].split("<br>");
				output += '<div class="estate_locator_detail_column_2 blocks_name">';
				$.each(estateNameBlockArr, function(index) {
					output += '<div class="estate_locator_detail_block_name"><div class="item__text">'+estateNameBlockArr[index]+'<br></div></div>';
				});
				output += '</div>';
			}else{
				if((key != "website")){
					if (estateObj[key][langCode] != null){
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">'+estateObj[key][langCode]+'</div></div>';
					} else {
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">-</div></div>';
					}
				} else {
					if (estateObj[key] != null){
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">'+estateObj[key]+'</div></div>';
					} else {
						output += '<div class="estate_locator_detail_column_2"><div class="item__text">-</div></div>';
					}
				}
			}
			output += '</div>';
		}
		break;
	}

	console.log(output);

    var estateImg = estateObj["image"];
	if (estateImg == '') {
		$(".estate_locator_fullwidth .estate_locator_detail_photo").attr({"style": "display:none"});
		$(".estate_locator_fullwidth .main_section_left .estate_locator_detail_photo.mobile").attr({"style": "display:none"});
	}
    $(".estate_locator_fullwidth .estate_locator_detail_photo").attr({"src": estateImg, "alt":getTxtByLang(["Picture: "+estateName,"相片: "+estateName,"相片: "+estateName])});
    $(".estate_locator_fullwidth .main_section_left .estate_locator_detail_photo.mobile").after(output);

	//initMap
	console.log("call load map");
	initReady = true;
    initMap(estateLocLat, estateLocLong);
}
// find estate object
function getEstateObjFun(estateJsonPath, estateIdPram, propId, distId){
	console.log(estateJsonPath);
	// get all object from json
    $.ajax({
        url: estateJsonPath,
        type: 'GET',
        dataType: "json",
        cache: false,
        async:false
    }).done(function (data) {
		console.log(data);
        var returnval = data;
        estateSearchReturnObj = [];
		// search each
        $.each(returnval, function(index) {
            var estateObj = returnval[index];
            var estateId = parseInt(estateObj["aplySysId"]);

			if (estateId === parseInt(estateIdPram)){
					estateSearchReturnObj = estateObj;
					return false;
				}

        })
        $(".estate_locator_topbar").show();
        $(".estate-locator-map-container").show();
        $(".search-estate-result").remove();
        loadInitEsateFun(estateSearchReturnObj, propId, distId);
    }).fail(function(data){
		console.log(data);
	})
}


function extraLinksSwitchFun(propertyId){
    switch(propertyId) {
        case 1:
            return '<a href="#" class="set_useful_a find_dist grey landing w-inline-block"><div>'+getTxtByLang(['Other estates in the same district', '區內其他屋邨', '区內其他屋邨'])+'</div></a><a href="/'+getShortLang()+'/global-elements/estate-locator/index.html?propId=1" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['Other districts', '其他地區', '其他地区'])+'</div></a>';
        case 2:
            return '<a href="#" class="set_useful_a find_dist grey landing w-inline-block"><div>'+getTxtByLang(['Other courts in the same district', '區內其他屋苑', '区內其他屋苑'])+'</div></a><a href="/'+getShortLang()+'/global-elements/estate-locator/index.html?propId=2" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['Other districts', '其他地區', '其他地区'])+'</div></a>';
        case 3:
            return '<a href="#" class="set_useful_a find_dist grey landing w-inline-block"><div>'+getTxtByLang(['Other shopping centres in the same region', '區內其他商場', '区內其他商场'])+'</div></a><a href="/'+getShortLang()+'/global-elements/estate-locator/index.html?propId=3" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['Other districts', '其他地區', '其他地区'])+'</div></a>';
        case 4:
            return '<a href="#" class="set_useful_a find_dist grey landing w-inline-block"><div>'+getTxtByLang(['Other Flatted Factories in the same region', '區內工廠大廈', '区內工厂大夏'])+'</div></a><a href="/'+getShortLang()+'/global-elements/estate-locator/index.html?propId=4" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['Other districts', '其他地區', '其他地区'])+'</div></a>';
        case 5:
            return '<a href="#" class="set_useful_a find_dist grey landing w-inline-block"><div>'+getTxtByLang(['Other commercial premise to lease in the same region', '區內商業場所租賃', '区內商业场所租赁'])+'</div></a><a href="/'+getShortLang()+'/global-elements/estate-locator/index.html?propId=5" class="set_useful_a grey landing w-inline-block"><div>'+getTxtByLang(['Other districts', '其他地區', '其他地区'])+'</div></a>';
        default:
            return false;
    }
}

function setUsefulFun(propertyId, extraLinksContent){
    $(".main_section_right .desktop_useful_links .useful_links_content .set_useful .set_useful_a").remove();
    $(".btn_quick_links_mobile_container .mobile_useful_link .set_useful .set_useful_a").remove();
    $(".main_section_right .desktop_useful_links .useful_links_content .set_useful_title").after(extraLinksContent);
    $(".main_section_right .desktop_useful_links .useful_links_content .set_useful .set_useful_a:last").attr({"data-ppt":propertyId});
    $(".main_section_right .desktop_useful_links .useful_links_content .set_useful .set_useful_a:nth-last-child(2)").attr({"data-ppt":propertyId});
    $(".btn_quick_links_mobile_container .mobile_useful_link .set_useful_title").after(extraLinksContent);
    $(".btn_quick_links_mobile_container .mobile_useful_link .set_useful .set_useful_a:last").attr({"data-ppt":propertyId});
    $(".btn_quick_links_mobile_container .mobile_useful_link .set_useful .set_useful_a:nth-last-child(2)").attr({"data-ppt":propertyId});
}

// load url prop
$(window).on('load',function(){
	setTimeout(function() {
		setLang();
		var propertyId = getUrlParameter('propId');
		if(propertyId == undefined){
			propertyId = getUrlParameter('propertyType');
		}
		var estateIdPram = getUrlParameter('id');
		if(estateIdPram == undefined){
			estateIdPram = getUrlParameter('id');
		}
		var districtId = getUrlParameter('dist');
		console.log(propertyId +" | "+ estateIdPram + " | " + districtId);
		var extraLinksContent = extraLinksSwitchFun(parseInt(propertyId));
		setUsefulFun(parseInt(propertyId), extraLinksContent);
		// get estate json path
		$.ajax({
			url: jsonInterPath+"/estate-locator-access.json",
			type: 'GET',
			dataType: "json",
			cache: false,
			async:false
		}).done(function (data) {
			var returnVal = data;
			estateAccessInitJson = returnVal;
			estateAccessRetunrObj = returnVal;
			var accessJsonPath;
			var regionJson;
			$.each(returnVal, function(index) {
				var propertyName = returnVal[index]["property"][langCode];
				$(".estate-property-area").append("<a href='#' class='w-dropdown-link' property='"+propertyName+"'>"+propertyName+"</a>");
				if(propertyId == returnVal[index]["id"]){
					// set estate json path
					accessJsonPath = returnVal[index]["estate"];
					//added 20190225
					if(districtId == undefined || districtId == ""){
						regionJson =  returnVal[index]["region"];
					}
					estatePorName = returnVal[index]["property"][langCode];
					var firstProperty = returnVal[index]["property"][langCode];
					$(".estate_locator_search_drop").find(".estate-property__text--choose").html(firstProperty);
					$(".estate_locator_search_drop").find(".estate-property__text--choose").attr("data-property", firstProperty);
				}
			});
			if(districtId == undefined || districtId == null || districtId == ""){
				findDistFromEstateID(jsonInterPath, regionJson , accessJsonPath, propertyId, estateIdPram);
			}else{
				console.log(districtId);
				estateJsonPath = jsonInterPath+accessJsonPath+districtId+".json";
				getEstateObjFun(estateJsonPath, estateIdPram, propertyId, districtId);
			}
		});
	}, 100);
})

function findDistFromEstateID(inJsonInterPath, inRegionJson, inAccessJsonPath, inPropertyID, inEstID){
	var jsonUrl = inJsonInterPath + inRegionJson;
	console.log(jsonUrl +" with estID: "+inEstID);

	 $.ajax({
        url: jsonUrl,
        type: 'GET',
        dataType: "json",
        cache: false,
        async:false
    }).done(function (data) {
		console.log(data);
		var regionArr = data["regionArray"];
		var dist = null;
		var isContinue = true;
		for(var regionCount = 0 ; regionCount < regionArr.length ; regionCount++ ){
			var districtArr = regionArr[regionCount]["district"];
			for(var distCount = 0; distCount < districtArr.length ; distCount++){
					console.log("Mark:");
					console.log(districtArr[distCount]["id"]);
					dist = districtArr[distCount]["id"];
					var estArr = districtArr[distCount]["estates"];
					console.log("estArray:");
					console.log(estArr);
					for(var estCount = 0; estCount < estArr.length ; estCount++){
						var estId = parseInt(estArr[estCount]["aplySysId"]);
						console.log(estId);
						if(estId == inEstID){
							isContinue = false;
							break;
						}
					}
					if(!isContinue){
						break;
					}
			}
			if(!isContinue){
				break;
			}
		}
		console.log("Finally: "+dist);
		var estateJsonPath = inJsonInterPath + inAccessJsonPath + dist + ".json";
		getEstateObjFun(estateJsonPath, inEstID, inPropertyID, dist);
	});

}

$(document).ready(function(){
    //click change property and ajax relative json
    $('.estate-property-area').on('click', '.w-dropdown-link', function(){
        var selectProVal = $(this).attr("property");
        $(this).closest(".prhtps_dropdown").find(".estate_locator_search_drop .estate-property__text--choose").html(selectProVal);
        $(this).closest(".prhtps_dropdown").trigger("w-close");
        locAccJsonArr = estateAccessRetunrObj[selectProVal];
    });

    //change estate property
    $('.estate_locator_property_type').on('click', '.estate-property-change-btn', function(){
		document.getElementById("map").style.display = 'block';
        var curProperty = $(this).closest(".estate_locator_property_type").find(".estate-property__text--choose").html();
        var propertyJsonId;
        $.each(estateAccessInitJson, function(index) {
            var propertyObj = estateAccessInitJson[index];
            var propertyName = propertyObj["property"][langCode];
            if(curProperty == propertyName){
                propertyJsonId = propertyObj["id"];
            }
        });
        var curUrl = window.location.href;
        var _curUrl = curUrl.substring(0, curUrl.lastIndexOf("/") + 1);
        window.location.href = _curUrl+"index.html?propId="+propertyJsonId;
    });

    //click quick link
    $(".useful_links_content .set_useful").on('click', '.set_useful_a.find_dist', function(){
        var propertyJsonId = $(this).attr("data-ppt");
        var districtVal = $(this).attr("data-dist");
        var curUrl = window.location.href;
        var _curUrl = curUrl.substring(0, curUrl.lastIndexOf("/") + 1);
        window.location.href = _curUrl+"index.html?propId="+propertyJsonId+"&distId="+districtVal;
    });

    //search estate
    $('.estate_locator_property_type').on('click', '.estate-locator-search-btn', function(){
        var searchKey = $(this).closest('.estate_locator_property_type').find('.keyword-input input').val();

		if (searchKey != undefined && searchKey != null && searchKey != "")
			searchKey = toHtmlEntities(searchKey);

        var searchResults=[];
        $.each(estateAccessRetunrObj, function(key, value) {
            var estateJsonObj = value;
            var propertyName = estateJsonObj["property"][langCode];
            var jsonFile = estateJsonObj["region"];
            var jsonPath = jsonInterPath+jsonFile;
            searchResult = searchEstate(jsonPath, propertyName, searchKey);
            searchResults.push(searchResult);
        });
        if(searchResults){
            listSearchResult(searchResults, searchKey);
        }
    });

    //click search result property
    $(".estate-locator-section").on('click', '.block_estate_locator--search-result .faq_rentpayment .faq_rentpayment_toggle', function(){
        if($(this).hasClass("w--open")){
            var $this = $(this).closest(".faq_rentpayment");
            $this.trigger("w-close");
            $this.find(".w-dropdown-toggle").trigger("w-close");
            $this.find(".w-dropdown-toggle").removeClass("w--open");
            $this.find(".w-dropdown-list").trigger("w-close");
            $this.find(".w-dropdown-list").removeClass("w--open");
		}else{
            $(this).addClass("w--open");
            $(this).closest(".faq_rentpayment").find(".w-dropdown-list").addClass("w--open");
        }
    });

    //click search result show map
    $(".estate-locator-section").on('click', '.block_estate_locator--search-result .faq_rentpayment_droplist .estate_locator_search_result_row .w-col-7', function(){
        var $this = $(this);
        var estateName = $(this).find(".estate_locator_search_result_name").html();
		var estateId = $(this).data("estId");
		var distId = $(this).data("distId");
        var propertyName = $(this).closest(".faq_rentpayment").find(".faq_rentpayment_toggle div").html();
        var accessJsonPath;
        var propId;
        $.each(estateAccessInitJson, function(index) {
            var initPorpertyName = estateAccessInitJson[index]["property"][langCode];
            if(propertyName == initPorpertyName){
                propId = estateAccessInitJson[index]["id"];
				var firstProperty = estateAccessInitJson[index]["property"][langCode];
				$(".estate_locator_search_drop").find(".estate-property__text--choose").html(firstProperty);
				$(".estate_locator_search_drop").find(".estate-property__text--choose").attr("data-property", firstProperty);
                accessJsonPath = estateAccessInitJson[index]["estate"];
                estatePorName = initPorpertyName;
            }
        });
        var extraLinksContent = extraLinksSwitchFun(parseInt(propId));
        setUsefulFun(parseInt(propId), extraLinksContent);

        estateJsonPath = jsonInterPath+accessJsonPath+distId+".json";
        getEstateObjFun(estateJsonPath, estateId, propId, distId);
		window.location.href="/"+getShortLang()+"/global-elements/estate-locator/detail.html?"+"propId="+propId+"&id="+estateId+"&dist="+distId
    });
})

function searchEstate(path, property, key){
    var searchPropertyObj = {};
    var searchKey = key;
    var propertyName = property;
    $.ajax({
        url: path,
        type: 'GET',
        dataType: "json",
        cache: false,
        async:false
    }).done(function (data) {
        var returnVal = data["regionArray"];
        var searchEstateObj = {};
        $.each(returnVal, function(index) {
           var areaObj = returnVal[index];
           var districtArr = areaObj["district"];
           $.each(districtArr, function(index) {
                var districtObj = districtArr[index];
                var districtName = districtObj["name"][langCode];
                var estatesArr = districtObj["estates"];
                var _estateArr = [];
                if(searchKey){
                    $.each(estatesArr, function(index) {
						var estate = {estId:"",distId:"",estName:""};
                        var estateName = estatesArr[index]["name"][langCode];
						var estateId = parseInt(estatesArr[index]["aplySysId"]);
                        if (estateName.toLowerCase().indexOf(searchKey.toLowerCase()) > -1){
							estate["distId"] = districtObj["id"];
							estate["estateId"] = estateId;
							estate["estName"] = estateName;
                            _estateArr.push(estate);
                            searchEstateObj[districtName]=_estateArr;
                        }
                    });
                }else{
                    $.each(estatesArr, function(index) {
						var estate = {estId:"",distId:"",estName:""};
						var estateId = parseInt(estatesArr[index]["aplySysId"]);
						estate["distId"] = districtObj["id"];
						estate["estateId"] = estateId;
						estate["estName"] = estatesArr[index]["name"][langCode];
                        _estateArr.push(estate);
                        searchEstateObj[districtName]=_estateArr;
                    });
                }
            });
        });
        if(!$.isEmptyObject(searchEstateObj)){
            searchPropertyObj[propertyName]=[];
            searchPropertyObj[propertyName].push(searchEstateObj);
        }
    });
    return searchPropertyObj;
}

function listSearchResult(val, key){
    $(".estate_locator_topbar").hide();
    $(".estate-locator-map-container").hide();
    $(".estate_locator_fullwidth .main_section_right").hide();
    $(".estate_locator_fullwidth .main_section_left").hide();
    $(".btn_quick_links_mobile_container").css("left", "-1000px");
    $(".estate_locator_topbar--search").remove();
    $(".block_estate_locator--search-result").remove();
	document.getElementById("map").style.display = 'none';

    var curUrl = window.location.href;
    var resultArr = val;
    var searchKey = key || '';
    var topBarOutput = '';
    topBarOutput += '<div class="estate_locator_topbar estate_locator_topbar--search w-clearfix">';
    topBarOutput += '<div class="estate_locator_search_result">'+getTxtByLang(['Search Result for', '搜索結果', '搜索结果'])+' "'+searchKey+'"</div>';
    topBarOutput += '</div>';
    var resultOutput = '';
    resultOutput += "<div class='block_estate_locator block_estate_locator--search-result'>";
    $.each(resultArr, function(index) {
        var itemObj = resultArr[index];
        if(!$.isEmptyObject(itemObj)){
            resultOutput += '<div data-delay="0" class="faq_rentpayment w-dropdown">';
            $.each(itemObj, function(key, value) {
                var propertyName = key;
                var regionArr = value;
                resultOutput += '<div class="faq_rentpayment_toggle estate_locator w-dropdown-toggle"><div>'+propertyName+'</div></div>';
                resultOutput += '<nav class="faq_rentpayment_droplist bp w-dropdown-list">';
                $.each(regionArr, function(index) {
                    var regionObj = regionArr[index];
                    var i = 0;
                    $.each(regionObj, function(key, value) {
                        var regionName = key;
                        var estatesArr = value;
                        if(estatesArr.length>0){
                            $.each(estatesArr, function(index) {
                                i++;
                                resultOutput += "<div class='estate_locator_search_result_row w-row'>";
                                resultOutput += '<div class="w-col w-col-7" data-est-Id="' + estatesArr[index]["estateId"] + '" data-dist-Id="' + estatesArr[index]["distId"] + '"><div class="estate_locator_search_result_name">'+estatesArr[index]["estName"]+'</div></div>';
                                resultOutput += '<div class="w-col w-col-5"><div class="row_contact_txt">'+regionName+'</div></div>';
                                resultOutput += "</div>"
                            });
                        }
                    });
                });
                resultOutput += "</nav>";
            });
            resultOutput += "</div>";
        }
    });
    resultOutput += "</div>";
    $( ".estate-locator-section .main_section_inner .main_section_left" ).append( topBarOutput );
    $( ".estate-locator-section .main_section_inner .estate_locator_fullwidth .main_section_left" ).after( resultOutput );
    var $customShowhide = $('.faq_rentpayment');
    $customShowhide.each(function (index) {
        var $thisDropdown = $(this);
        var $thisToggle = $thisDropdown.find('.w-dropdown-toggle');
        var $thisList = $thisDropdown.find('.w-dropdown-list');
        if (index == 0) {
            $thisToggle.trigger("click");
            if (!$thisToggle.hasClass('w--open')) {
                $thisToggle.addClass('w--open');
                $thisList.addClass('w--open');
            }
        }
    });
}

/**
 * Convert a string to HTML entities
 */
 /*
String.prototype.toHtmlEntities = function() {
    return this.replace(/./gm, function(s) {
        // return "&#" + s.charCodeAt(0) + ";";
        return (s.match(/[a-z0-9\s]+/i)) ? s : "&#" + s.charCodeAt(0) + ";";
    });
};*/

function toHtmlEntities(searchValue)
{
 
   if(searchValue.indexOf("<") != -1 || searchValue.indexOf(">") != -1){
	  searchValue = searchValue.replaceAll(">","&gt;").replaceAll("<", "&lt;");
	  return searchValue;
   }else{
	  return searchValue;
   }
};

/**
 * Create string from HTML entities
 */
String.fromHtmlEntities = function(string) {
    return (string+"").replace(/&#\d+;/gm,function(s) {
        return String.fromCharCode(s.match(/\d+/gm)[0]);
    })
};