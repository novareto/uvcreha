$(document).ready(function() {
	$("#portal-globalnav").prepend('<li id="portaltab-burger-menu"><i class="glyphicon glyphicon-menu-hamburger" /></li>'),
		$("body").on("mousemove", function(e) {
			e.pageX < 20 && $("body").attr("data-with-sidebar", "true")
		}),
		$("#portaltab-burger-menu").click(function(e) {
			e.preventDefault(),
				$("body").attr("data-with-sidebar", "true")
		}),
		$("#portal-navigation-cover").click(function(e) {
			e.preventDefault(),
				$("body").attr("data-with-sidebar", "")
		})
})
$(document).ready(function () {

  // Custom JavaScript
  function nearTo($element, distance, side, event) {
    var left = $element.offset().left;
    var loffset = left + distance;
    var right = left + $element.width();
    var roffset = right - distance;
    var x = event.pageX;
    if (side == 'left') {
      return x < loffset;
    };
    if (side == 'right') {
      return x > roffset;
    };
  };

  function showSidebar() {
    $('#portal-navigation-cover').fadeIn('500');
    $('body').attr('data-with-sidebar', 'true');    
  }

  function hideSidebar() {
    $('#portal-navigation-cover').fadeOut('500');
    $('body').attr('data-with-sidebar', 'false');
  }


    // Mouse
    $('body').mousemove(function (event) {
      var nav = $('#portal-navigation');
      var offset = 30;
      if (nav.hasClass('sidebar-left')) {
        var nearby = nearTo(nav, offset, 'left', event);
        if (nearby) {
          showSidebar();
        };
      } else {
        var nearby = nearTo(nav, offset, 'right', event);
        if (nearby) {
          showSidebar();
        };
      };
    });

    // Burger


    $('#portal-navigation-cover').click(function (e) {
      e.preventDefault();
      hideSidebar();
    });



  $('#sidebar-handle').click(function (e) {
    e.preventDefault();
    showSidebar();
  });


  // Fileinput
  $("input[type=file]").fileinput();

});
