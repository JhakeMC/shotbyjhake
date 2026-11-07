/* ==========================================================================
   THIS IS THE ONLY FILE YOU NEED TO EDIT TO UPDATE YOUR WEBSITE.

   HOW TO ADD PHOTOS
   1. Put the photo file inside the "images" folder (e.g. images/wedding-01.jpg).
   2. Add its path to the list you want, e.g. "images/wedding-01.jpg",
      (keep the quotes and the comma).
   Photos can also be a web link (https://...). To add a caption/alt text for
   screen readers, write { src: "images/wedding-01.jpg", alt: "Bride laughing" }.

   HOW TO ADD A PROJECT OR EVENT
   Copy one whole { ... }, block inside "projects" or "events", paste it right
   after, and change the text. The site sorts them by date (newest first) on
   its own, so the order in this file does not matter.
   Dates are written YYYY-MM-DD, for example 2026-12-25.
   ========================================================================== */

const G = "https://sites.google.com/sitesv-images-rt/"; // old Google Sites image host (see README to replace these)

const SITE = {
  name: "Jhake Togonon",
  brand: "Jhake Does Photography",
  roles: ["Portrait Photographer", "Event Photographer", "Street Photographer"],
  tagline: "Capturing moments. Telling stories.",

  email: "jhake.tgnnwork@gmail.com",
  phone: "09919297864",
  instagram: { handle: "jhake.tgnn", url: "https://www.instagram.com/jhake.tgnn/" },
  facebook: "https://www.facebook.com/jhake.does.photography",
  midnightSuite: "https://drive.google.com/drive/folders/1BRoCBwuXRJQJEMF16dgKah76my-dEN8m?usp=sharing", // set to "" to hide the button

  intro: {
    projects: "Shoots and productions I have been part of.",
    events: "Workshops and events I have shot or joined."
  },

  /* Three photos for the home page collage at the top */
  hero: [
    G + "AMxu72veSn6uO-gUYrZUhxUCCZHmaAsOtx6CK8hf4SW-T3xKAoQRzrZe07wx1ZcnK_-dfVlSqyF27EAGqEcHuO5f56bKghjjQ79PiKGltHhRejIOmxi8GQYpU3kckFT3B49PZjlYsIEPkCl7xbWqYp4VOGWgnfkn4ZIxwgWy-Gv2VqNlwnGajEEPOsNhs1ge3PGaTVknuuoSQAZuA2lP_XWAOiVG1FbJIc8AXI7OWO_w818=w1280",
    G + "AMxu72t3L8ddjeNM0WLUzVgnyUOH4kaXFvh7H1IUeFl6oHgn4dZ91m3xfZYDGyU3Fc5gmq4gSD5zIPrh7aLcK94-l2ictJEcT_iC576cSsKk-FgS65cVOE2_KeaXWoDbgIwDfQVh0Fj3EQb7XnW5sjDtiJunGZ7mdJgVFvkfUqYTkaqhD8miLAb_SUJEMCMwmvOMhyRAP8mlBvAtKZjDZFuP5-QV9PkNskdwA7doy4hWEt4=w1280",
    G + "AMxu72tT43VHIKBikuv0qBAn_LfIpY5NyjRAQtC39ScKlW9pDSE3z23FaQt_WLDtG-KjOgV2DHELQIU5S_hEdjbQVD3b6Zob84uSzXhVfybvHCxsylF7YFuckaDnKSDSMDGJ1_SXx9ZDJKWdIv2f2y4FsVnyvJjKopOzwTt_3gN6K-ktWpAUuVkq_NdN8CU8js9G3AjWTDT88BHETNgt3Z7AF8u3jFaeN74ziutnSsV7=w1280"
  ],

  /* HOME PAGE HIGHLIGHTS: add as many photos as you like. Newest at the bottom or top, your choice. */
  highlights: [
    G + "AMxu72veSn6uO-gUYrZUhxUCCZHmaAsOtx6CK8hf4SW-T3xKAoQRzrZe07wx1ZcnK_-dfVlSqyF27EAGqEcHuO5f56bKghjjQ79PiKGltHhRejIOmxi8GQYpU3kckFT3B49PZjlYsIEPkCl7xbWqYp4VOGWgnfkn4ZIxwgWy-Gv2VqNlwnGajEEPOsNhs1ge3PGaTVknuuoSQAZuA2lP_XWAOiVG1FbJIc8AXI7OWO_w818=w1280",
    G + "AMxu72t3L8ddjeNM0WLUzVgnyUOH4kaXFvh7H1IUeFl6oHgn4dZ91m3xfZYDGyU3Fc5gmq4gSD5zIPrh7aLcK94-l2ictJEcT_iC576cSsKk-FgS65cVOE2_KeaXWoDbgIwDfQVh0Fj3EQb7XnW5sjDtiJunGZ7mdJgVFvkfUqYTkaqhD8miLAb_SUJEMCMwmvOMhyRAP8mlBvAtKZjDZFuP5-QV9PkNskdwA7doy4hWEt4=w1280",
    G + "AMxu72tT43VHIKBikuv0qBAn_LfIpY5NyjRAQtC39ScKlW9pDSE3z23FaQt_WLDtG-KjOgV2DHELQIU5S_hEdjbQVD3b6Zob84uSzXhVfybvHCxsylF7YFuckaDnKSDSMDGJ1_SXx9ZDJKWdIv2f2y4FsVnyvJjKopOzwTt_3gN6K-ktWpAUuVkq_NdN8CU8js9G3AjWTDT88BHETNgt3Z7AF8u3jFaeN74ziutnSsV7=w1280",
    G + "AMxu72u75o3WY7qzInQQ-d44Wt_TkhJDm2iZd28b5kdZodF6wFCNj-usfgPLpFwDE5fXajbs45pJtctV7fWxla8zfZ0YFa2B9OiQLFlrDfjAdGL7NbIud5rgJZottzQMdSoJ-SKFtMM1fLVx_8Cf5M-oPQ9HFAkE3gT2lNtBeZKcpxSmpFNpsaW9la8Jb6zD1CNMHSowX36kcQgbgFcbE-mERNJE67yo0hRJsZfq6GLHdPA=w1280",
    G + "AMxu72sj26GvmKouLfQYugHF5PVJIod6txIDT8j7GORJxjb0MnzJGseUDpkQDHXxIQboF4DWp2YSHoxBT3LDNr1Z5VEww0LHrWXsMpmm-YqARRLoMx2MT-au5wuoKSIzVF9gMrn_8aBDeVAP3XR7QCAt9yOUSQXpU_bGxwIfkN9z0KLJ5M_dlpTJeFADHWwOWqTV76UE_E4GKcAE_eTZNATl19SC5vnISfBYl518VpatZEk=w1280",
    G + "AMxu72t0i1RLX0QUjoI3nmMaYy6l6oWstWVHh1zu9xHpo4bl7gl3X-mdN1xpFHk5s3SL_MNBtXfbQRT-iObH5zyw_PBqAJzuE2Sy2_eJnG4fv8hChcWMuFlI7gYkldzGI4lFY014GwNL5ef5YNOD7f9rHhBBY7lFxkMicq9jwShv7u3YKSjTOAv0pw0V-OJp3AJg17cpXgd7zmtfTjat2zgmw-m8tA5-RCze_vNNWeLb3Sc=w1280"
    // add more here, e.g.  "images/my-new-photo.jpg",
  ],

  about: {
    photo: G + "AMxu72vBgCR7c6SI6Gkj_eyjktzIDB2RoCVqZHVESaOh2eAbrfbDp7_dMw0IDPPBpbMQgBzPo_7WeKeimT0dViIHYP-VlEvd-EsSrFCPadmxbX_sCl1fvcJliL60QoEJgncOnf_COSaLZtsD4bBOQ-eVIFPFNan1j8bjlRPFPpLUELogfYSAXhWDbrr4q_Sg=w1280",
    heading: "My Background",
    bio: [
      "I’m a self-taught photographer currently freelancing jobs to help finance my studies. I’ve gotten my experience from events I joined or at open shows.",
      "Before photography, I had quite a programming background making Discord bots, then became a cyclist and now a marathoner. I do some reading here and there, and my favorite book is “Atomic Habits” by James Clear."
    ],
    experience: [
      { date: "2026-10-22", title: "Canon Wedding Photography Workshop", role: "By Kenneth Hao & Ian Celis" },
      { date: "2026-10-03", title: "Aliana Samulde’s Debut", role: "SDE Editor, in collaboration with Northlight Productions" },
      { date: "2026-09-17", title: "Ellen Jamandre’s Pre-debut Photoshoot", role: "Photographer" },
      { date: "2026-05-31", title: "@afterdawncommunity x Butter & Spoon 2", role: "Photographer" }
    ],
    education: [
      { years: "2025 - 2027", school: "Stratford International School", note: "Asst. EIC, The Globe Publication" },
      { years: "2021 - 2025", school: "Fatima National High School", note: "SPA, Media Arts" }
    ]
  },

  /* PROJECTS: copy a whole block to add one. "images" are the photos shown in its gallery. */
  projects: [
    {
      title: "Aliana@XVIII",
      subtitle: "A full package deal with Northlight Productions for Aliana’s debut coverage.",
      date: "2026-10-03",
      text: [
        "Aliana’s decade and eight debut celebration. A moment worth remembering, from the journey towards a bright future.",
        "I am the SDE Editor for the whole event. It was a team collaboration with RZ Aperture and SignatureVisuals as Northlight Productions. We have captured a transitional moment in Aliana’s journey, the blooming of a bright future ahead, and a day worth remembering."
      ],
      images: [
        G + "AMxu72uwPbBBkWVNrUkuyfaHBrKMwafh6zY06TJ1rfEuAxPFhz0iK2Rr98KAkjtWjWchaMFV-_XPfPARt9HWDb2ns3tRPq382Ol4pYQTXBIOaQuTZOinkm15QJX4rgZ6_SDjiSKgslZzcKGcgbaK4vn-SLfo6tMMj_on6WibLbxgx8afpVGg5pWlab_weBeiVAhyRC6aOBYdnGQVCwD2-07pO_ONERRORyAsUjiMc43RIZA=w1280",
        G + "AMxu72sunyIrmmp2pyQOwpq_htczbPuvnYzgnkkXu4phfawMSJ2kk6x8nSiAPNtEt_b9hG16N0z8mjGu0bisnF-d9URh8cj2V3Pz3LH6c-lAkMuWFIEUy882phO_KJWuGB8La5QHbbFtJaTy982mzeQbyzMygb2uG5PCRkA9be5hTr1vkKqvUpTxMlnEHNMyzKbVbv4FsT-UNrrJq_SGr2veWlB0Ub5SWd5vacrCdvye=w1280",
        G + "AMxu72vQ11VrDLq8x62VwdRyQ4-iz5qV7iIHmRZL5TBG0hCNOpONr7EMH_PsSM1HcKs-AyJi4cx9GuXAlsv1fwJoWwTYlH3MQbhN6E-sIfBFgBoP6wL1FpP_8oIZ7cYMttzUQNNHI6tvOEdPOUxdFHzRAuEAafHL9wksDsh78_ZD0XiK4oaFOlK7yyrUPtyjM_LK2sHzsYwCAq5RS00f0Ujqm8IHWLBhDls8uu0FcGAg4W0=w1280"
      ]
    },
    {
      title: "Ellen@XVIII",
      subtitle: "A pre-debut photoshoot for a young gal’s special day.",
      date: "2026-09-17",
      text: [
        "The day before legality. A day where Ellen shines brighter than ever, captured in a flash, leaning to a future with much more opportunities to offer.",
        "I am the pre-debut photographer. Capturing such a fleeting moment in one’s beautiful journey in life is such a pleasure, taking in the time before entering legality."
      ],
      images: [
        G + "AMxu72uTWhwR18RUxQ4_7b_0Q1vf4G4AiCvPkbW-djHf_-wDzVrQXIhqZcb4okWrzHyOupmCSjiQGehgFlIFgqkjOh3v-xupEdk6BETVdg6zTGNwaaJKsWSvUAEKau7z9lAP1gUQFtJfoK5vaMR4CdiIfUMlzjQLuSyYbGz6f1a5GpYFtXbAqCaClai-CGXoPCjKZcfjIQyhVOH6usmW-NYipW5HyQSJZEMa-tMA8sNx04E=w1280",
        G + "AMxu72uL3iV62Pn3uzqNCYycb1cCDx_Bg42W8r0XAeDThA6pln0xLhHa79M3ZCWiO-lV8c-RZdF-7NkdtlkCpikIEGNVzrqIp9m4xCPm3gJ3wA1DLwAU0vMQqwfkQYKjGhh9dojPRJQraLF39AYTLsspBKsq65kHK6jGOEZVYpLfRlMTDVItJxHXLwH0XsMCwwIq_O2Geuu4v2e0SUu8kdhmF_xQ8ikgXUDdDhSLzaFI=w1280",
        G + "AMxu72vlzE4re32c82PmJkPb_JBkeK7j3dEZP18GPy5gbg1MPEXBitoyGbfLZovVlayXkKDZCW4eDlJu3jx1E-oEtq0hWv3ShU2yIgtsDQ79_aM_C-A6EkjfmlFqZXMp3gpMn1zFa-IRq0lhI-56ZeZKVE13HI9YiJ7arR7u57DdlTC0Ue4-KyMgSR5d3-KPEDFePQStnkg6PDspXJAzCnsjskrEhrySbBUm6sJTyMhDCCQ=w1280"
      ]
    }
  ],

  /* EVENTS: same idea as projects. "sections" is optional and splits an event into parts, each with its own photos. */
  events: [
    {
      title: "Canon Wedding Masterclass: Capturing love through light, composition and film.",
      subtitle: "Wedding photography and filmmaking skills with Canon Brand Ambassadors Kenneth Hao and Ian Celis.",
      date: "2026-10-22",
      images: [
        G + "AMxu72sXtO1mNVwM0hG0dQSWvggeHfkKNZsEEW3oADPTYc3oh0h0Xb9UFXOBv_XaM6ePNr-dn8h2gyWlgWc9pgUUWEVZOvwRGY358kTGp-Go9oRK0yKXi3Q2-c28axJ0nOzWADwAbIOO8I7qGuYqjVlmw1ttfiYVnvhDsLmhSwuolD2FuO7M5lvXEdiaN4P2jed0bCug7pBdeRdVSd9hYweqJKLHc_ppEqADzIHBBzxk4N4=w1280",
        G + "AMxu72vgm4s-N8l7hxshhlECzn_16_FEwgb8KIeUr2QlEmfvH3z9o9lpxiuvsvH-iYHs4mjTSczoJfmgYhXuWYO8BE7X84zOR5WmfiSudLLKSuWQ4Tlg1Vtbg3S_At5YTuuSjG1VXZS9QWZ3nCk55q6GGRKyiQGQU39PXn5bNSd-lBqfBvwFq1a8ahEGZ-vwnr8W-Ctn66t16D3fvkUfzL0AXgNFfSn5cpVJ1Ry3VN103Dw=w1280",
        G + "AMxu72sTvbWM4Ocug0_XmCYlTeRq1saYtPFf1YNGwsYIp0RHX1myI7pdVl1xz7xfQj8nLvmbA6w6ZrG1X1dcPIKqvOroFTvW1R7JzLLywTexJxOyZUaMsAjZdBgQT5hpbTq32xgosbG-C_eNtRLdNWzoPbAbtkWmI_dUcCpgooSbzdCtoJQB5l6sY4Cbo-MS3Vgl8ctGDVJ--2xiK-vjjL4WnFJR1jSAXBIN7PgkGhQa=w1280"
      ],
      sections: [
        {
          title: "Part I: Portrait Session and Lighting with Kenneth Hao",
          text: ["Every love story deserves to be captured beautifully.", "A day of learning, creating, and seeing love through the lens."],
          images: [
            G + "AMxu72tYvaBcNFYiK9U4nof2MLLEbND7YfNfkeTyC0YHtpWA_zH3By-7S82nt8S6DILpekwsQwizxuMWvHqL0EapaGLwSrE2XYSJnP7T5NpyNWqNvrNJerrdn2zY2Yxus0gT5Cvs03ijl37xgThTziAAC1Z7G4Y2pO8OqZSh9i51HkOxnOc9pM_xuyJkzoIKAmfSh69L2TnAC_NzZtHhIeoJj72uUyJ0oWxcDgG4Dd3khM4=w1280",
            G + "AMxu72sWr9PtySDbV8jTfExJp0I3IfwgWjrLpkEbVUedLlt8BgYp2WW2h5yobCrENkOi_1nx0cW3T4Xn5-ltCfu0bvXtv0wj1nmfRMSD4TwJ1FxfSmwXTxqeCIjG9oCBPahdzNHPAcetpIaFTkMJWHXpHG7WvSDWslkEzdOL87_bGtZmJ8-EW0q_H7Qs9C6U13AAzplNhOB5eROi3DoJ03CcH2Kr5ZBQG7HBRjPpnICSzWo=w1280"
          ]
        },
        {
          title: "Part II: Wedding Filmmaking with Ian Celis",
          text: ["Every love story has a story worth telling.", "In Part II of the Wedding Masterclass, filmmaker Ian Celis guided participants through the art of wedding filmmaking, exploring creative techniques to capture authentic emotions, beautiful moments, and unforgettable love stories in motion."],
          images: []
        }
      ]
    }
  ]
};
