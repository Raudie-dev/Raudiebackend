/**
 * RauDie Landing Page JavaScript - Versión Optimizada
 * Mejoras de rendimiento y funcionalidad
 */

document.addEventListener("DOMContentLoaded", () => {
  // =============================================
  // FUNCIONES UTILITARIAS OPTIMIZADAS
  // =============================================

  function debounce(func, wait = 20, immediate = false) {
    let timeout
    return function (...args) {
      const later = () => {
        timeout = null
        if (!immediate) func.apply(this, args)
      }
      const callNow = immediate && !timeout
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
      if (callNow) func.apply(this, args)
    }
  }

  // Cache de elementos DOM para mejor rendimiento
  const elements = {
    mobileToggle: document.querySelector(".mobile-toggle"),
    navMenu: document.querySelector(".nav-menu"),
    scrollTop: document.getElementById("scroll-top"),
    filterBtns: document.querySelectorAll(".filter-btn"),
    projects: document.querySelectorAll(".project-card"),
    whatsappBtn: document.querySelector(".whatsapp-btn"),
    contactForm: document.querySelector(".contact-form"),
  }

  // =============================================
  // MENÚ MÓVIL OPTIMIZADO
  // =============================================

  if (elements.mobileToggle && elements.navMenu) {
    let menuOverlay = document.querySelector(".menu-overlay")
    if (!menuOverlay) {
      menuOverlay = document.createElement("div")
      menuOverlay.className = "menu-overlay"
      document.body.appendChild(menuOverlay)
    }

    function toggleMenu(e) {
      e?.preventDefault()
      const isActive = elements.navMenu.classList.contains("active")

      elements.navMenu.classList.toggle("active")
      elements.mobileToggle.classList.toggle("active")
      menuOverlay.classList.toggle("active")
      document.body.style.overflow = isActive ? "" : "hidden"
    }

    function closeMenu() {
      elements.navMenu.classList.remove("active")
      elements.mobileToggle.classList.remove("active")
      menuOverlay.classList.remove("active")
      document.body.style.overflow = ""
    }

    elements.mobileToggle.addEventListener("click", toggleMenu)
    menuOverlay.addEventListener("click", closeMenu)

    // Submenús móviles optimizados
    document.querySelectorAll(".has-submenu > a").forEach((item) => {
      item.addEventListener("click", function (e) {
        if (window.innerWidth <= 768) {
          e.preventDefault()
          const parent = this.parentElement
          const wasActive = parent.classList.contains("active")

          // Cerrar otros submenús
          document.querySelectorAll(".has-submenu.active").forEach((other) => {
            if (other !== parent) other.classList.remove("active")
          })

          parent.classList.toggle("active", !wasActive)
        }
      })
    })

    // Cerrar menú al hacer clic en enlaces
    document.querySelectorAll(".nav-menu a:not(.has-submenu > a)").forEach((link) => {
      link.addEventListener("click", closeMenu)
    })
  }

  // =============================================
  // FORMULARIO DE CONTACTO OPTIMIZADO
  // =============================================

document.addEventListener("DOMContentLoaded", () => {
  const contactForm = document.querySelector(".contact-form");

  if (contactForm) {
    contactForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const form = e.target;
      const formData = new FormData(form);
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;

      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
      submitBtn.disabled = true;

      try {
        const response = await fetch("send_email.php", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
          submitBtn.innerHTML = '<i class="fas fa-check"></i> ¡Enviado!';
          submitBtn.style.background = "#10b981";
          form.reset();
        } else {
          throw new Error(result.message || "Error desconocido en el servidor.");
        }
      } catch (error) {
        submitBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
        submitBtn.style.background = "#ef4444";
        alert("Error al enviar el mensaje: " + error.message);
      } finally {
        setTimeout(() => {
          submitBtn.innerHTML = originalText;
          submitBtn.disabled = false;
          submitBtn.style.background = "";
        }, 2000);
      }
    });
  }
});

  // =============================================
  // SCROLL TO TOP OPTIMIZADO
  // =============================================

  if (elements.scrollTop) {
    const toggleScrollButton = debounce(() => {
      elements.scrollTop.classList.toggle("active", window.scrollY > 100)
    }, 100)

    window.addEventListener("scroll", toggleScrollButton, { passive: true })
    toggleScrollButton()

    elements.scrollTop.addEventListener("click", (e) => {
      e.preventDefault()
      window.scrollTo({ top: 0, behavior: "smooth" })
    })
  }

  // =============================================
  // FILTRADO DE PROYECTOS OPTIMIZADO
  // =============================================

  if (elements.filterBtns.length && elements.projects.length) {
    function filterProjects(filter) {
      const fragment = document.createDocumentFragment()

      elements.projects.forEach((project) => {
        const categories = project.dataset.category?.split(" ") || []
        const shouldShow = filter === "all" || categories.includes(filter)

        if (shouldShow) {
          project.style.display = "block"
          project.classList.add("visible")
        } else {
          project.classList.remove("visible")
          project.style.display = "none"
        }
      })
    }

    elements.filterBtns.forEach((btn) => {
      btn.addEventListener("click", function () {
        // Remover clase active de todos los botones
        elements.filterBtns.forEach((b) => b.classList.remove("active"))
        this.classList.add("active")
        filterProjects(this.dataset.filter)
      })
    })

    // Inicializar con todos los proyectos visibles
    filterProjects("all")
  }

  // =============================================
  // MODALES OPTIMIZADOS CON LAZY LOADING
  // =============================================

  function setupOptimizedModals() {
    const modals = new Map()

    function createModal(modalId) {
      if (modals.has(modalId)) return modals.get(modalId)

      const modal = document.querySelector(modalId)
      if (!modal) return null

      const modalData = {
        element: modal,
        thumbnails: modal.querySelectorAll(".thumbnail"),
        mainImage: modal.querySelector(".gallery-main img"),
        prevBtn: modal.querySelector(".prev-btn"),
        nextBtn: modal.querySelector(".next-btn"),
        currentSlide: modal.querySelector(".current-slide"),
        totalSlides: modal.querySelector(".total-slides"),
        currentIndex: 0,
      }

      modals.set(modalId, modalData)
      return modalData
    }

    function openModal(modalId) {
      const modalData = createModal(modalId)
      if (!modalData) return

      modalData.element.classList.add("active")
      document.body.style.overflow = "hidden"
      setupModalGallery(modalData)
    }

    function closeModal(modal) {
      if (modal) {
        modal.classList.remove("active")
        document.body.style.overflow = ""
      }
    }

    function setupModalGallery(modalData) {
      const { thumbnails, mainImage, prevBtn, nextBtn, currentSlide, totalSlides } = modalData

      if (totalSlides) totalSlides.textContent = thumbnails.length

      function updateImage(index) {
        if (!thumbnails[index] || !mainImage) return

        const thumbnail = thumbnails[index]
        const imageUrl = thumbnail.dataset.image

        if (imageUrl && imageUrl !== mainImage.src) {
          // Lazy loading de imágenes
          const img = new Image()
          img.onload = () => {
            mainImage.src = imageUrl
          }
          img.src = imageUrl
        }

        thumbnails.forEach((thumb, i) => {
          thumb.classList.toggle("active", i === index)
        })

        if (currentSlide) currentSlide.textContent = index + 1
        modalData.currentIndex = index
      }

      // Event listeners optimizados
      thumbnails.forEach((thumb, index) => {
        thumb.addEventListener("click", () => updateImage(index))
      })

      if (prevBtn) {
        prevBtn.addEventListener("click", () => {
          const newIndex = (modalData.currentIndex - 1 + thumbnails.length) % thumbnails.length
          updateImage(newIndex)
        })
      }

      if (nextBtn) {
        nextBtn.addEventListener("click", () => {
          const newIndex = (modalData.currentIndex + 1) % thumbnails.length
          updateImage(newIndex)
        })
      }

      // Inicializar con la primera imagen
      if (thumbnails.length > 0) updateImage(0)
    }

    // Event delegation para mejor rendimiento
    document.addEventListener("click", (e) => {
      if (e.target.matches(".view-details") || e.target.closest(".view-details")) {
        e.preventDefault()
        const btn = e.target.matches(".view-details") ? e.target : e.target.closest(".view-details")
        const modalId = `#projectModal${btn.dataset.project}`
        openModal(modalId)
      }

      if (e.target.matches(".modal-close") || e.target.closest(".modal-close")) {
        e.preventDefault()
        const modal = e.target.closest(".modern-modal")
        closeModal(modal)
      }

      if (e.target.matches(".modal-backdrop")) {
        const modal = e.target.closest(".modern-modal")
        closeModal(modal)
      }
    })

    // Cerrar con tecla Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        document.querySelectorAll(".modern-modal.active").forEach(closeModal)
      }
    })
  }

  setupOptimizedModals()

  // =============================================
  // WHATSAPP OPTIMIZADO
  // =============================================

  if (elements.whatsappBtn) {
    let notification = document.querySelector(".whatsapp-notification")
    if (!notification) {
      notification = document.createElement("div")
      notification.className = "whatsapp-notification"
      notification.innerHTML = `
        <div class="notification-header">
          <i class="fab fa-whatsapp notification-icon"></i>
          <div class="notification-title">WhatsApp</div>
        </div>
        <div class="notification-message">¡Envíanos un mensaje para atención inmediata!</div>
      `
      document.body.appendChild(notification)
    }

    let notificationTimeout

    const showNotification = () => {
      clearTimeout(notificationTimeout)
      notification.classList.add("show")
    }

    const hideNotification = () => {
      notificationTimeout = setTimeout(() => {
        notification.classList.remove("show")
      }, 500)
    }

    elements.whatsappBtn.addEventListener("mouseenter", showNotification)
    elements.whatsappBtn.addEventListener("mouseleave", hideNotification)
    notification.addEventListener("mouseenter", showNotification)
    notification.addEventListener("mouseleave", hideNotification)

    // Mostrar notificación inicial
    setTimeout(() => {
      showNotification()
      setTimeout(hideNotification, 3000)
    }, 2000)
  }

  // =============================================
  // SCROLL SUAVE OPTIMIZADO
  // =============================================

  document.addEventListener("click", (e) => {
    const anchor = e.target.closest('a[href^="#"]:not([href="#"])')
    if (!anchor) return

    if (anchor.parentElement.classList.contains("has-submenu") && window.innerWidth <= 768) return

    e.preventDefault()
    const target = document.querySelector(anchor.getAttribute("href"))

    if (target) {
      const headerHeight = document.querySelector(".header")?.offsetHeight || 0
      const targetPosition = target.offsetTop - headerHeight

      window.scrollTo({
        top: targetPosition,
        behavior: "smooth",
      })
    }
  })

  // =============================================
  // FORMULARIO OPTIMIZADO
  // =============================================

  if (elements.contactForm) {
    elements.contactForm.addEventListener("submit", async (e) => {
      e.preventDefault()

      const submitBtn = elements.contactForm.querySelector('button[type="submit"]')
      const originalText = submitBtn.innerHTML

      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...'
      submitBtn.disabled = true

      try {
        // Simular envío (aquí irían las validaciones reales)
        await new Promise((resolve) => setTimeout(resolve, 1500))

        submitBtn.innerHTML = '<i class="fas fa-check"></i> ¡Enviado!'
        submitBtn.style.background = "#10b981"

        setTimeout(() => {
          submitBtn.innerHTML = originalText
          submitBtn.disabled = false
          submitBtn.style.background = ""
          elements.contactForm.reset()
        }, 2000)
      } catch (error) {
        submitBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error'
        submitBtn.style.background = "#ef4444"

        setTimeout(() => {
          submitBtn.innerHTML = originalText
          submitBtn.disabled = false
          submitBtn.style.background = ""
        }, 2000)
      }
    })
  }

  // =============================================
  // ANIMACIONES DE SCROLL OPTIMIZADAS
  // =============================================

  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible")
        observer.unobserve(entry.target) // Dejar de observar una vez visible
      }
    })
  }, observerOptions)

  // Observar elementos que necesitan animación
  document.querySelectorAll(".project-card, .service-card").forEach((el) => {
    observer.observe(el)
  })

  console.log("RauDie Website - Optimización completada ✅")
})


    // Minimal modal open/close and thumbnail handling for dynamically generated modals
    document.addEventListener('click', function (e) {
      // open modal
      var openBtn = e.target.closest('.open-project-modal');
      if (openBtn) {
        var target = openBtn.dataset.target;
        var modal = document.querySelector(target);
        if (modal) {
          modal.style.display = 'block';
          modal.classList.add('open');
          document.body.style.overflow = 'hidden';
        }
        return;
      }

      // close modal via close button
      var closeBtn = e.target.closest('.modal-close');
      if (closeBtn) {
        var modal = closeBtn.closest('.modern-modal');
        if (modal) {
          modal.style.display = 'none';
          modal.classList.remove('open');
          document.body.style.overflow = '';
        }
        return;
      }

      // close when clicking backdrop
      if (e.target.classList && e.target.classList.contains('modal-backdrop')) {
        var modal = e.target.closest('.modern-modal');
        if (modal) {
          modal.style.display = 'none';
          modal.classList.remove('open');
          document.body.style.overflow = '';
        }
      }
    });

    // thumbnails: change main image when clicking thumbnail
    document.addEventListener('click', function (e) {
      var thumb = e.target.closest('.thumbnail');
      if (!thumb) return;
      var modal = thumb.closest('.modern-modal');
      if (!modal) return;
      var mainImg = modal.querySelector('.gallery-main img');
      if (!mainImg) return;
      var src = thumb.dataset.image;
      if (src) mainImg.src = src;
      modal.querySelectorAll('.thumbnail').forEach(function (t) { t.classList.remove('active'); });
      thumb.classList.add('active');
    });