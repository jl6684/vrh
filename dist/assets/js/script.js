$(function() {
    // $('#header-include').load('https://codrkai.github.io/header.html');
    // $('#footer-include').load('https://codrkai.github.io/footer.html');

    $(window).scroll(function() {
        if ( $(this).scrollTop() > 100 ) {
            $('.navbar').addClass('solid bg-dark');
        } else {
            $('.navbar').removeClass('solid bg-dark');
        }
    });

    // This script has been moved to footer.html because since I'm
    // using the javascript load() function above, this now needs to 
    // run after everthing is loaded.
    // If you are not using the load() function above, then uncomment 
    // the function below and it will work the same way.
    
     $('a[href^="#"]').on('click', function(e) {
        if ( this.hash !== "" ) {
            e.preventDefault();
            var anchor = this.hash;

            $('html, body').animate({
                scrollTop: $(anchor).offset().top
            }, 800, function() {
                window.location.hash = anchor;
            });
        }
    });

    // Contact form handling
    $('#contactForm').on('submit', function(e) {
        e.preventDefault();
        
        // Simple form validation
        let isValid = true;
        $(this).find('[required]').each(function() {
            if (!$(this).val()) {
                isValid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        if (isValid) {
            // Simulate form submission
            alert('Thank you for your message! We\'ll get back to you within 24 hours.');
            this.reset();
        }
    });
    
});
