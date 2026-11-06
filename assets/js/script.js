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

    // =============================================
  // MENÚ MÓVIL & DRAWER MODERNO
  // =============================================
  const modernMobileBtn = document.querySelector(".mobile-menu-btn");
  const modernDrawer = document.querySelector(".mobile-drawer");
  const modernOverlay = document.querySelector(".mobile-drawer-overlay");
  const modernCloseBtn = document.querySelector(".drawer-close");

  function openModernDrawer() {
    modernDrawer?.classList.add("active");
    modernOverlay?.classList.add("active");
    document.body.style.overflow = "hidden";
  }

  function closeModernDrawer() {
    modernDrawer?.classList.remove("active");
    modernOverlay?.classList.remove("active");
    document.body.style.overflow = "";
  }

  if (modernMobileBtn) {
    modernMobileBtn.addEventListener("click", openModernDrawer);
  }
  if (modernCloseBtn) {
    modernCloseBtn.addEventListener("click", closeModernDrawer);
  }
  if (modernOverlay) {
    modernOverlay.addEventListener("click", closeModernDrawer);
  }
  document.querySelectorAll(".drawer-links a").forEach(link => {
    link.addEventListener("click", closeModernDrawer);
  });

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

  if (elements.contactForm) {
    elements.contactForm.addEventListener("submit", async (e) => {
      e.preventDefault()

      const submitBtn = elements.contactForm.querySelector('button[type="submit"]')
      const originalText = submitBtn.innerHTML

      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...'
      submitBtn.disabled = true

      try {
        const name = document.getElementById("contactName")?.value || "";
        const phone = document.getElementById("contactPhone")?.value || "";
        const email = document.getElementById("contactEmail")?.value || "";
        const message = document.getElementById("contactMessage")?.value || "";

        // First, save to database
        const formData = new FormData(elements.contactForm);
        // Add CSRF Token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        
        await fetch("/guardar-contacto/", {
          method: "POST",
          headers: {
            'X-CSRFToken': csrfToken
          },
          body: formData,
        });

        // Format the WhatsApp message
        const text = `Hola RauDie! Me gustaría obtener más información.
Mis datos son:
- Nombre: ${name}
- Teléfono: ${phone}
- Email: ${email}

Mensaje:
${message}`;

        // Phone number configured on the page
        const targetPhone = "5491172341870";
        const whatsappUrl = `https://wa.me/${targetPhone}?text=${encodeURIComponent(text)}`;

        window.open(whatsappUrl, "_blank");

        // Reset the form and button
        elements.contactForm.reset();
        submitBtn.innerHTML = '<i class="fas fa-check"></i> ¡Enviado!'
        submitBtn.style.background = "#10b981"

        setTimeout(() => {
          submitBtn.innerHTML = originalText
          submitBtn.disabled = false
          submitBtn.style.background = ""
        }, 2000)
        
      } catch (error) {
        submitBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error'
        submitBtn.style.background = "#ef4444"
        console.error("Error en formulario:", error)

        setTimeout(() => {
          submitBtn.innerHTML = originalText
          submitBtn.disabled = false
          submitBtn.style.background = ""
        }, 2000)
      }
    })
  }

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
        elements.filterBtns.forEach((b) => b.classList.remove("active"))
        this.classList.add("active")
        filterProjects(this.dataset.filter)
      })
    })

    filterProjects("all")
  }

  // =============================================
  // MODALES OPTIMIZADOS
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

      if (thumbnails.length > 0) updateImage(0)
    }

    // Event delegation para modales
    document.addEventListener("click", (e) => {
      const trigger = e.target.closest(".view-details, .project-card")
      if (trigger) {
        const isCardChild = e.target.closest('a, button'); // ignore links/buttons inside card
        if (trigger.matches('.project-card') && isCardChild && isCardChild !== trigger) {
            return;
        }
        e.preventDefault()
        let project = trigger.dataset.project;
        if (!project && trigger.closest('.project-card')) {
             project = trigger.closest('.project-card').dataset.project;
        }
        if (project) {
             const modalId = `#projectModal${project}`
             openModal(modalId)
        }
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

      // Abrir modales dinámicos
      if (e.target.matches(".open-project-modal") || e.target.closest(".open-project-modal")) {
        e.preventDefault()
        const btn = e.target.matches(".open-project-modal") ? e.target : e.target.closest(".open-project-modal")
        const target = btn.dataset.target
        const modal = document.querySelector(target)
        if (modal) {
          modal.style.display = "block"
          modal.classList.add("open")
          document.body.style.overflow = "hidden"
        }
      }

      // Cerrar mediante close button
      if (e.target.matches(".modal-close") || e.target.closest(".modal-close")) {
        const modal = e.target.closest(".modern-modal")
        if (modal) {
          modal.style.display = "none"
          modal.classList.remove("open")
          document.body.style.overflow = ""
        }
      }

      // Cerrar mediante backdrop
      if (e.target.classList && e.target.classList.contains("modal-backdrop")) {
        const modal = e.target.closest(".modern-modal")
        if (modal) {
          modal.style.display = "none"
          modal.classList.remove("open")
          document.body.style.overflow = ""
        }
      }
    })

    // Cerrar con Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        document.querySelectorAll(".modern-modal.active").forEach(closeModal)
      }
    })
  }

  setupOptimizedModals()

  // =============================================
  // THUMBNAILS EN MODALES
  // =============================================

  document.addEventListener("click", (e) => {
    const thumb = e.target.closest(".thumbnail")
    if (!thumb) return

    const modal = thumb.closest(".modern-modal")
    if (!modal) return

    const mainImg = modal.querySelector(".gallery-main img")
    if (!mainImg) return

    const src = thumb.dataset.image
    if (src) mainImg.src = src

    modal.querySelectorAll(".thumbnail").forEach((t) => {
      t.classList.remove("active")
    })
    thumb.classList.add("active")
  })

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

    setTimeout(() => {
      showNotification()
      setTimeout(hideNotification, 3000)
    }, 2000)
  }

  // =============================================
  // SCROLL SUAVE OPTIMIZADO
  // =============================================

  document.addEventListener("click", (e) => {
    const anchor = e.target.closest('a[href*="#"]:not([href="#"])')
    if (!anchor) return

    if (anchor.parentElement && anchor.parentElement.classList.contains("has-submenu") && window.innerWidth <= 768) return

    // Verify if the link points to the current page
    const href = anchor.getAttribute("href");
    const hashIndex = href.indexOf('#');
    const path = href.substring(0, hashIndex);
    const hash = href.substring(hashIndex);
    
    // Only smooth scroll if we are on the same path (or path is empty meaning it's a direct anchor)
    if (path === "" || path === window.location.pathname) {
      e.preventDefault()
      const target = document.querySelector(hash)

      if (target) {
        const headerHeight = document.querySelector(".header")?.offsetHeight || 0
        const targetPosition = target.offsetTop - headerHeight

        window.scrollTo({
          top: targetPosition,
          behavior: "smooth",
        })
      }
    }
  })

  // =============================================
  // ANIMACIÓN DE MÉTRICAS (CONTADORES)
  // =============================================
  const metricNumbers = document.querySelectorAll('.metric-number');
  let animationStarted = false;

  if (metricNumbers.length > 0) {
    const startCounting = () => {
      metricNumbers.forEach(counter => {
        const target = +counter.getAttribute('data-target');
        const duration = 2000; // 2 seconds
        const increment = target / (duration / 16); // ~60fps

        let current = 0;
        const updateCounter = () => {
          current += increment;
          if (current < target) {
            counter.innerText = Math.ceil(current);
            requestAnimationFrame(updateCounter);
          } else {
            counter.innerText = target;
          }
        };
        updateCounter();
      });
    };

    const metricsObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !animationStarted) {
          animationStarted = true;
          startCounting();
        }
      });
    }, { threshold: 0.5 });

    const metricsSection = document.querySelector('.metrics-section');
    if (metricsSection) {
      metricsObserver.observe(metricsSection);
    }
  }

  // =============================================
  // HORIZONTAL ACCORDION (MOBILE CLICK SUPPORT)
  // =============================================
  const accCards = document.querySelectorAll('.acc-card');
  if (accCards.length > 0) {
    accCards.forEach(card => {
      card.addEventListener('click', () => {
        // Remove active from all
        accCards.forEach(c => c.classList.remove('active'));
        // Add active to clicked
        card.classList.add('active');
      });
    });
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
        observer.unobserve(entry.target)
      }
    })
  }, observerOptions)

  document.querySelectorAll(".project-card, .service-card").forEach((el) => {
    observer.observe(el)
  })

  console.log("RauDie Website - Optimización completada ✅")
})
