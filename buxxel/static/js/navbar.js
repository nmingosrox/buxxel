let lastScrollTop = 0;
const slidingContent = document.getElementById("nav-top-content");

window.addEventListener("scroll", function() {
  let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  let contentHeight = slidingContent.offsetHeight;

  if (scrollTop > lastScrollTop && scrollTop > 50) {
    // Scrolling down → Slide the top rows up
    slidingContent.style.marginTop = `-${contentHeight}px`; 
  } else {
    // Scrolling up → Slide them back down
    slidingContent.style.marginTop = "0";
  }
  lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
}, false);
