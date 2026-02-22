// Utility: Add smooth scrolling and animations
document.addEventListener("DOMContentLoaded", () => {
    // ========== NAVBAR MOBILE TOGGLE ==========
    const navbarToggle = document.querySelector(".navbar-toggle")
    const navbarNav = document.querySelector(".navbar-nav")
    
    if (navbarToggle && navbarNav) {
      navbarToggle.addEventListener("click", (e) => {
        e.stopPropagation()
        navbarNav.classList.toggle("show")
        navbarToggle.classList.toggle("active")
      })
    }
  
    // ========== DROPDOWN MENU MOBILE ==========
    const dropdownItems = document.querySelectorAll(".nav-item.has-dropdown")
    dropdownItems.forEach((item) => {
      const link = item.querySelector(".nav-link")
      if (link) {
        link.addEventListener("click", (e) => {
          if (window.innerWidth <= 768) {
            e.preventDefault()
            item.classList.toggle("show")
          }
        })
      }
    })
  
    // ========== CLOSE MENU ON LINK CLICK ==========
    const navLinks = document.querySelectorAll(".navbar-nav .nav-link")
    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        if (!link.parentElement.classList.contains("has-dropdown")) {
          navbarNav.classList.remove("show")
          navbarToggle.classList.remove("active")
        }
      })
    })
  
    // ========== CLOSE MENU WHEN CLICKING OUTSIDE ==========
    document.addEventListener("click", (e) => {
      if (!e.target.closest(".admin-header")) {
        navbarNav.classList.remove("show")
        if (navbarToggle) navbarToggle.classList.remove("active")
        dropdownItems.forEach((item) => item.classList.remove("show"))
      }
    })

    // ========== IMPROVED MOBILE MENU TOGGLE (LEGACY) ==========
    const menuToggle = document.querySelector(".menu-toggle")
    const navList = document.querySelector(".nav-list")
  
    if (menuToggle && navList) {
      menuToggle.addEventListener("click", function () {
        this.classList.toggle("active")
        navList.classList.toggle("active")
      })
  
      // Close menu when clicking on a nav link
      const navLinks = document.querySelectorAll(".nav-list a")
      navLinks.forEach((link) => {
        link.addEventListener("click", () => {
          menuToggle.classList.remove("active")
          navList.classList.remove("active")
        })
      })
  
      // Close menu when clicking outside
      document.addEventListener("click", (event) => {
        const isClickInsideNav = navList.contains(event.target)
        const isClickOnToggle = menuToggle.contains(event.target)
  
        if (navList.classList.contains("active") && !isClickInsideNav && !isClickOnToggle) {
          menuToggle.classList.remove("active")
          navList.classList.remove("active")
        }
      })
    }
  
    // Header scroll effect
    const header = document.querySelector(".header")
    window.addEventListener("scroll", () => {
      if (window.scrollY > 50) {
        header.classList.add("scrolled")
      } else {
        header.classList.remove("scrolled")
      }
    })
  
    // Initialize all sliders
    initializeAllSliders()
  
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        e.preventDefault()
  
        const targetId = this.getAttribute("href")
        const targetElement = document.querySelector(targetId)
  
        if (targetElement) {
          const headerHeight = document.querySelector(".header").offsetHeight
          const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight
  
          window.scrollTo({
            top: targetPosition,
            behavior: "smooth",
          })
        }
      })
    })
  
    // Active menu item based on scroll position
    const sections = document.querySelectorAll("section")
    const navLinks = document.querySelectorAll(".nav-list a")
  
    window.addEventListener("scroll", () => {
      let current = ""
      const headerHeight = document.querySelector(".header").offsetHeight
  
      sections.forEach((section) => {
        const sectionTop = section.offsetTop - headerHeight - 100
        const sectionHeight = section.offsetHeight
  
        if (window.pageYOffset >= sectionTop) {
          current = section.getAttribute("id")
        }
      })
  
      navLinks.forEach((link) => {
        link.classList.remove("active")
        if (link.getAttribute("href") === `#${current}`) {
          link.classList.add("active")
        }
      })
    })
  
    // Add animation classes on scroll
    const animateElements = document.querySelectorAll(
      ".mission-content, .vision-content, .extension-card, .birthday-card, .event-card",
    )
  
    function checkIfInView() {
      animateElements.forEach((element) => {
        const elementTop = element.getBoundingClientRect().top
        const windowHeight = window.innerHeight
  
        if (elementTop < windowHeight - 100) {
          element.classList.add("fade-in")
        }
      })
    }
  
    // Initial check
    checkIfInView()
  
    // Check on scroll
    window.addEventListener("scroll", checkIfInView)
  
    // Add staggered animation delays to extension cards
    const extensionCards = document.querySelectorAll(".extension-card")
    extensionCards.forEach((card, index) => {
      const delay = (index % 3) * 100
      card.classList.add(`delay-${delay}`)
    })
  
    // Function to initialize all sliders on the page
    function initializeAllSliders() {
      // Get all birthday slider containers on the page
      const birthdaySliders = document.querySelectorAll(".birthday-slider")
  
      birthdaySliders.forEach((sliderContainer) => {
        const container = sliderContainer.querySelector(".slider-container")
        const prevBtn = sliderContainer.querySelector(".prev-btn")
        const nextBtn = sliderContainer.querySelector(".next-btn")
        const cards = container.querySelectorAll(".birthday-card")
  
        if (container && prevBtn && nextBtn && cards.length > 0) {
          let currentIndex = 0
          const cardCount = cards.length
  
          // Set initial position
          updateSlider()
  
          // Event listeners for slider controls
          prevBtn.addEventListener("click", () => {
            currentIndex = (currentIndex - 1 + cardCount) % cardCount
            updateSlider()
          })
  
          nextBtn.addEventListener("click", () => {
            currentIndex = (currentIndex + 1) % cardCount
            updateSlider()
          })
  
          // Function to update slider position
          function updateSlider() {
            const translateValue = -currentIndex * 100 + "%"
            container.style.transform = `translateX(${translateValue})`
  
            // Add active class to current card
            cards.forEach((card, index) => {
              if (index === currentIndex) {
                card.classList.add("active")
  
                // Create confetti effect for active card
                createConfetti(card)
              } else {
                card.classList.remove("active")
  
                // Remove confetti from inactive cards
                const confetti = card.querySelector(".confetti")
                if (confetti) {
                  confetti.innerHTML = ""
                }
              }
            })
          }
  
          // Create confetti effect
          function createConfetti(card) {
            const iconContainer = card.querySelector(".birthday-icon-container")
            if (!iconContainer) return
  
            let confetti = iconContainer.querySelector(".confetti")
  
            if (!confetti) {
              confetti = document.createElement("div")
              confetti.className = "confetti"
              iconContainer.appendChild(confetti)
            }
  
            confetti.innerHTML = ""
  
            // Add confetti particles
            for (let i = 0; i < 5; i++) {
              const span = document.createElement("span")
              span.style.left = `${Math.random() * 100}%`
              span.style.animationDuration = `${2 + Math.random() * 2}s`
              span.style.animationDelay = `${Math.random() * 0.5}s`
              confetti.appendChild(span)
            }
          }
  
          // Add touch swipe functionality for mobile
          let touchStartX = 0
          let touchEndX = 0
  
          container.addEventListener("touchstart", (e) => {
            touchStartX = e.changedTouches[0].screenX
          })
  
          container.addEventListener("touchend", (e) => {
            touchEndX = e.changedTouches[0].screenX
            handleSwipe()
          })
  
          function handleSwipe() {
            const swipeThreshold = 50
            if (touchEndX < touchStartX - swipeThreshold) {
              // Swipe left - next slide
              nextBtn.click()
            } else if (touchEndX > touchStartX + swipeThreshold) {
              // Swipe right - previous slide
              prevBtn.click()
            }
          }
  
          // Auto-advance slides every 5 seconds
          let slideInterval = setInterval(() => {
            nextBtn.click()
          }, 5000)
  
          // Pause auto-advance on hover
          sliderContainer.addEventListener("mouseenter", () => {
            clearInterval(slideInterval)
          })
  
          sliderContainer.addEventListener("mouseleave", () => {
            slideInterval = setInterval(() => {
              nextBtn.click()
            }, 5000)
          })
        }
      })
  
      // Initialize events slider
      const eventsSlider = document.querySelector(".events-slider")
  
      if (eventsSlider) {
        const container = eventsSlider.querySelector(".slider-container")
        const prevBtn = eventsSlider.querySelector(".prev-btn")
        const nextBtn = eventsSlider.querySelector(".next-btn")
        const eventItems = container.querySelectorAll(".event-item")
  
        if (container && prevBtn && nextBtn && eventItems.length > 0) {
          let currentIndex = 0
          const itemCount = eventItems.length
  
          // Set initial position
          updateEventsSlider()
  
          // Event listeners for slider controls
          prevBtn.addEventListener("click", () => {
            currentIndex = (currentIndex - 1 + itemCount) % itemCount
            updateEventsSlider()
          })
  
          nextBtn.addEventListener("click", () => {
            currentIndex = (currentIndex + 1) % itemCount
            updateEventsSlider()
          })
  
          // Function to update slider position
          function updateEventsSlider() {
            const translateValue = -currentIndex * 100 + "%"
            container.style.transform = `translateX(${translateValue})`
  
            // Add active class to current item
            eventItems.forEach((item, index) => {
              if (index === currentIndex) {
                item.classList.add("active")
              } else {
                item.classList.remove("active")
              }
            })
          }
  
          // Add touch swipe functionality for mobile
          let touchStartX = 0
          let touchEndX = 0
  
          container.addEventListener("touchstart", (e) => {
            touchStartX = e.changedTouches[0].screenX
          })
  
          container.addEventListener("touchend", (e) => {
            touchEndX = e.changedTouches[0].screenX
            handleSwipe()
          })
  
          function handleSwipe() {
            const swipeThreshold = 50
            if (touchEndX < touchStartX - swipeThreshold) {
              // Swipe left - next slide
              nextBtn.click()
            } else if (touchEndX > touchStartX + swipeThreshold) {
              // Swipe right - previous slide
              prevBtn.click()
            }
          }
  
      // Auto-advance slides every 6 seconds
          let slideInterval = setInterval(() => {
            nextBtn.click()
          }, 6000)
  
          // Pause auto-advance on hover
          eventsSlider.addEventListener("mouseenter", () => {
            clearInterval(slideInterval)
          })
  
          eventsSlider.addEventListener("mouseleave", () => {
            slideInterval = setInterval(() => {
              nextBtn.click()
            }, 6000)
          })
        }
      }
    }
  
    // ========== TABLE ROW HOVER EFFECTS ==========
    const tableRows = document.querySelectorAll("table tbody tr")
    tableRows.forEach((row) => {
      row.addEventListener("mouseenter", () => {
        row.style.transform = "scale(1.01)"
        row.style.boxShadow = "inset 3px 0 0 rgba(192, 19, 30, 0.5)"
      })
      row.addEventListener("mouseleave", () => {
        row.style.transform = "scale(1)"
        row.style.boxShadow = "none"
      })
    })
  
    // ========== MODAL ANIMATION IMPROVEMENTS ==========
    const modals = document.querySelectorAll(".modal")
    modals.forEach((modal) => {
      modal.addEventListener("show.bs.modal", () => {
        modal.style.animation = "fadeIn 0.3s ease-out"
      })
    })
  
    // ========== FORM INPUT FOCUS EFFECTS ==========
    const formControls = document.querySelectorAll(".form-control, .form-select")
    formControls.forEach((input) => {
      input.addEventListener("focus", () => {
        input.parentElement.classList.add("focused")
        input.style.boxShadow =
          "0 0 0 4px rgba(192, 19, 30, 0.1), 0 0 0 1px rgba(192, 19, 30, 1)"
      })
      input.addEventListener("blur", () => {
        input.parentElement.classList.remove("focused")
        input.style.boxShadow = "none"
      })
    })
  
    // ========== BUTTON RIPPLE EFFECT ==========
    const buttons = document.querySelectorAll(".btn")
    buttons.forEach((button) => {
      button.addEventListener("click", function (e) {
        const ripple = document.createElement("span")
        const rect = this.getBoundingClientRect()
        const size = Math.max(rect.width, rect.height)
        const x = e.clientX - rect.left - size / 2
        const y = e.clientY - rect.top - size / 2
  
        ripple.style.width = ripple.style.height = size + "px"
        ripple.style.left = x + "px"
        ripple.style.top = y + "px"
        ripple.classList.add("ripple")
  
        this.appendChild(ripple)
  
        setTimeout(() => ripple.remove(), 600)
      })
    })
  
    // ========== BADGE ANIMATIONS ==========
    const badges = document.querySelectorAll(".badge")
    badges.forEach((badge, index) => {
      badge.style.animation = `fadeIn 0.4s ease-out ${index * 0.05}s both`
    })
  
    // ========== TOOLTIP INITIALIZATION ==========
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      if (typeof bootstrap !== "undefined" && bootstrap.Tooltip) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
      }
    })
  
    // ========== SCROLL ANIMATIONS ==========
    const scrollElements = document.querySelectorAll(".card, .table-responsive")
    const elementInView = (el, dividend = 1) => {
      const elementTop = el.getBoundingClientRect().top
      return elementTop <= (window.innerHeight || document.documentElement.clientHeight) / dividend
    }
  
    const displayScrollElement = (element) => {
      element.classList.add("fade-in")
    }
  
    const hideScrollElement = (element) => {
      element.classList.remove("fade-in")
    }
  
    window.addEventListener("scroll", () => {
      scrollElements.forEach((el) => {
        if (elementInView(el, 1.25)) {
          displayScrollElement(el)
        }
      })
    })
  })
  
