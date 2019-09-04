

function checkHost() {
	return window.location.href.startsWith("https://tinder.com/app/recs");
}

var first_time = true;
var counter = 0;
var rand_number=1000;
function swipeBot() {
	
	//below is to like a photo
	//getElementsByClassName(className)[0].click();
	//below to unlike a photo
	var imageCardParent = 'recCard Ov(h) Cur(p) W(100%) Bgc($c-placeholder) StretchedBox Bdrs(8px) CenterAlign--ml Toa(n) active';
	
	//var infoButton = 'Pos(a) End(16px) B(40px) Trsdu($normal) Sq(40px) Lh(40px) Bdrs(50%) Cur(p) Ta(c) Fl(end) Scale(1.2):h';
	//document.getElementsByClassName(infoButton)[0].click()
	//need to add delay random
	//var randomPeriod = getRandomWait();
	//setTimeout(swipeBot, randomPeriod)
	
	//var rightPhotoSlider = 'Pos(a) Z(1) T(50%) End(0) Mx(10px) Op(0) tappable-view:h_Op(1) Trsdu($fast) Rotate(180deg) D(n)--s';
 	//console.log(document.getElementsByClassName(rightPhotoSlider));
	//document.getElementsByClassName(rightPhotoSlider)[0].click(); 
/* 	var new_slider = "profileCard__slider__imgShadow"; //this  did not cause a click
	document.getElementsByClassName(new_slider)[0].click(); */
	//var lifestyle = "recCard Ov(h) Cur(p) W(100%) Bgc($c-placeholder) StretchedBox Bdrs(8px) CenterAlign--ml Toa(n) active";
	//console.log (document.getElementsByClassName(lifestyle));
	//document.getElementsByClassName(lifestyle).click(); 
	/* 
	var upper_scroller = "bullet D(ib) Va(m) Cnt($blank)::a D(b)::a H(4px)::a W(100%)::a Py(6px) Px(2px) W(100%) Bdrs(100px)::a Bgc($c-bg-black)::a Op(.2)";
	console.log(document.getElementsByClassName(upper_scroller));
	document.getElementsByClassName(upper_scroller).click(); */
	


	

	if (first_time == true){
		first_time = false;
		rand_number = getRandomi();
		rand_number = rand_number %17;
	}

	if (counter == rand_number){
		//now swipe left'
		counter  = 0;
		//var element = document.querySelector('[aria-label="Nope"]').click();
		var className = 'button Lts($ls-s) Z(0) Cur(p) Tt(u) Bdrs(50%) P(0) Fw($semibold) recsGamepad__button D(b) Bgc(#fff) Wc($transform) Start(15px) Scale(1.1):h';
		document.getElementsByClassName(className)[0].click();
		rand_number = getRandomi();
		rand_number = rand_number %17;
	}
	else {
		//swipe right 
		var className = 'button Lts($ls-s) Z(0) Cur(p) Tt(u) Bdrs(50%) P(0) Fw($semibold) recsGamepad__button D(b) Bgc(#fff) Wc($transform) End(15px) Scale(1.1):h';
		document.getElementsByClassName(className)[0].click();
		counter++;
	}
		
	
	
	
	// If reached max likes per day then show modal and get it's content...
	// Check if there is any subscription button...
	if (document.getElementsByClassName('productButton__subscriptionButton').length > 0) {
		// counter object
		var hms = document.getElementsByClassName('Fz($ml)')[0].textContent;
		// Split it at the colons
		var a = hms.split(':');
		// Minutes are worth 60 seconds. Hours are worth 60 minutes. 1 second = 1kmilliseconds
		var seconds = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2])
		
		return seconds * 1000;
	}
}

function getRandomPeriod() {
	return Math.round(Math.random() * (2000 - 500)) + 500;
}

function getRandomWait() {
	return Math.round(Math.random() * (1000 - 200)) + 500;
}

function getRandomi (){
	return Math.round(Math.random()*8);
}

(function MainLoop() {
	// A random period between 500ms and 2secs
	var randomPeriod = getRandomPeriod();
	setTimeout(function() {
		randomPeriod = undefined;
		if (checkHost()) {
			var delay	= swipeBot();
			if (delay) {
				console.log('Too many likes for now, have to wait: ' + delay + ' ms');
				randomPeriod = delay;
			}
		}
		if (!randomPeriod) {
			MainLoop();
		}
		else {
			setTimeout(MainLoop, randomPeriod);
		}
	}, randomPeriod);
}());