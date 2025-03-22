window.onload = function() {
    // Si la página ya ha cargado una vez, no mostrar el loader
    if (!localStorage.getItem('loaderShown')) {
        // Mostrar el loader solo cuando la página se esté cargando
        document.querySelector('.wrapper').style.display = 'block';
        document.getElementById('content').style.display = 'none';
        
        // Después de que la página se haya cargado completamente (2.4 segundos o el tiempo que desees)
        setTimeout(function() {
            document.querySelector('.wrapper').style.display = 'none';
            document.getElementById('content').style.display = 'block';
            
            // Guardar en localStorage que el loader ya fue mostrado
            localStorage.setItem('loaderShown', 'true');
        }, 2400); // El loader se mostrará durante 2.4 segundos
    } else {
        // Si el loader ya fue mostrado, solo muestra el contenido
        document.querySelector('.wrapper').style.display = 'none';
        document.getElementById('content').style.display = 'block';
    }
  };