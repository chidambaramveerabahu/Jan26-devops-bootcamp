from flask import Flask, render_template_string

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Akhilesh Mishra &mdash; DevOps Engineer &amp; Educator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0f172a;
            color: #e2e8f0;
            line-height: 1.7;
        }

        /* ── Nav ── */
        nav {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid #1e293b;
            padding: 16px 0;
        }
        nav ul {
            list-style: none;
            max-width: 900px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            justify-content: center;
            gap: 32px;
        }
        nav a {
            color: #94a3b8;
            text-decoration: none;
            font-size: 0.9rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            transition: color 0.2s;
        }
        nav a:hover { color: #7dd3fc; }

        /* ── Hero ── */
        .hero {
            text-align: center;
            padding: 100px 24px 80px;
            max-width: 780px;
            margin: 0 auto;
        }
        .hero .badge {
            display: inline-block;
            background: #1e293b;
            border: 1px solid #334155;
            color: #7dd3fc;
            font-size: 0.82rem;
            padding: 6px 14px;
            border-radius: 20px;
            margin-bottom: 24px;
            letter-spacing: 0.04em;
        }
        .hero h1 {
            font-size: 3.2rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 12px;
            line-height: 1.2;
        }
        .hero h1 span { color: #7dd3fc; }
        .hero .subtitle {
            font-size: 1.15rem;
            color: #94a3b8;
            margin-bottom: 8px;
        }
        .hero .location {
            color: #64748b;
            font-size: 0.92rem;
            margin-bottom: 32px;
        }
        .hero .cta-row {
            display: flex;
            justify-content: center;
            gap: 14px;
            flex-wrap: wrap;
        }
        .btn {
            display: inline-block;
            padding: 10px 22px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            text-decoration: none;
            transition: transform 0.15s, box-shadow 0.15s;
        }
        .btn:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(0,0,0,0.3); }
        .btn-primary { background: #7dd3fc; color: #0f172a; }
        .btn-outline { border: 1px solid #334155; color: #cbd5e1; }

        /* ── Section shared ── */
        section { padding: 72px 24px; max-width: 900px; margin: 0 auto; }
        .section-title {
            font-size: 1.6rem;
            color: #f1f5f9;
            margin-bottom: 8px;
        }
        .section-sub {
            color: #64748b;
            font-size: 0.95rem;
            margin-bottom: 40px;
        }
        .divider {
            width: 44px; height: 3px;
            background: #7dd3fc;
            border-radius: 2px;
            margin-bottom: 12px;
        }

        /* ── Stats ── */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
            margin-bottom: 56px;
        }
        .stat-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 28px 16px;
            text-align: center;
        }
        .stat-card .num {
            font-size: 2rem;
            font-weight: 700;
            color: #7dd3fc;
        }
        .stat-card .label {
            font-size: 0.82rem;
            color: #64748b;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* ── About ── */
        .about-text {
            color: #cbd5e1;
            font-size: 1.02rem;
            max-width: 720px;
        }
        .about-text p { margin-bottom: 16px; }
        .about-text strong { color: #f1f5f9; }

        /* ── Skills ── */
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
        }
        .skill-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 24px;
        }
        .skill-card h4 {
            color: #7dd3fc;
            font-size: 0.88rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 14px;
        }
        .tag-row { display: flex; flex-wrap: wrap; gap: 8px; }
        .tag {
            background: #0f172a;
            border: 1px solid #334155;
            color: #94a3b8;
            font-size: 0.8rem;
            padding: 4px 10px;
            border-radius: 6px;
        }

        /* ── Projects ── */
        .projects-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 20px;
        }
        .project-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 24px;
            text-decoration: none;
            color: inherit;
            transition: border-color 0.2s;
            display: block;
        }
        .project-card:hover { border-color: #7dd3fc; }
        .project-card h4 { color: #f1f5f9; margin-bottom: 6px; font-size: 1rem; }
        .project-card p { color: #64748b; font-size: 0.88rem; margin-bottom: 10px; }
        .project-card .stars { color: #7dd3fc; font-size: 0.82rem; }

        /* ── Content / Writing ── */
        .writing-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
        }
        .writing-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 24px;
            text-decoration: none;
            color: inherit;
            transition: border-color 0.2s;
            display: block;
        }
        .writing-card:hover { border-color: #7dd3fc; }
        .writing-card .platform-badge {
            display: inline-block;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #7dd3fc;
            margin-bottom: 10px;
        }
        .writing-card h4 { color: #f1f5f9; font-size: 0.95rem; margin-bottom: 6px; }
        .writing-card p { color: #64748b; font-size: 0.85rem; }

        /* ── Connect ── */
        .connect-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 14px;
        }
        .connect-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 18px 16px;
            text-decoration: none;
            color: #cbd5e1;
            font-size: 0.88rem;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: border-color 0.2s, background 0.2s;
        }
        .connect-card:hover { border-color: #7dd3fc; background: #253347; }
        .connect-card .icon { font-size: 1.2rem; }

        /* ── Footer ── */
        footer {
            text-align: center;
            padding: 48px 24px;
            border-top: 1px solid #1e293b;
            color: #475569;
            font-size: 0.85rem;
        }
        footer a { color: #7dd3fc; text-decoration: none; }

        /* ── Responsive ── */
        @media (max-width: 600px) {
            .hero h1 { font-size: 2.2rem; }
            nav ul { gap: 18px; }
        }
    </style>
</head>
<body>


<!-- Nav -->
<nav>
    <ul>
        <li><a href="#about Akhilesh">About</a></li>
        <li><a href="#skills">Skills</a></li>
        <li><a href="#projects">Projects</a></li>
        <li><a href="#writing">Writing</a></li>
        <li><a href="#connect">Connect</a></li>
    </ul>
</nav>

<!-- Hero -->
<header class="hero">
    <div class="badge">&#9679; AWS Community Builder</div>
    <h1>Akhilesh <span>Mishra</span></h1>
    <p class="subtitle">Senior DevOps Engineer &amp; Educator</p>
    <p class="location">Noida / New Delhi, India &nbsp;&#8226;&nbsp; NIT Srinagar Alumni</p>
    <div class="cta-row">
        <a href="https://livingdevops.com" class="btn btn-primary" target="_blank">LivingDevOps</a>
        <a href="https://github.com/akhileshmishrabiz" class="btn btn-outline" target="_blank">GitHub</a>
        <a href="https://topmate.io/akhilesh_mishra" class="btn btn-outline" target="_blank">Book a Session</a>
    </div>
</header>

<!-- Stats -->
<section>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="num">13+</div>
            <div class="label">Years Experience</div>
        </div>
        <div class="stat-card">
            <div class="num">800+</div>
            <div class="label">Professionals Mentored</div>
        </div>
        <div class="stat-card">
            <div class="num">4.9</div>
            <div class="label">Mentoring Rating</div>
        </div>
        <div class="stat-card">
            <div class="num">17K+</div>
            <div class="label">Medium Followers</div>
        </div>
    </div>
</section>

<!-- About -->
<section id="about">
    <div class="divider"></div>
    <h2 class="section-title">About Me</h2>
    <p class="section-sub">The story behind LivingDevOps</p>
    <div class="about-text">
        <p>
            I started my career in <strong>Linux support</strong> and taught myself DevOps the hard way —
            spending <strong>5&ndash;6 hours every day for five months</strong> learning Docker, cloud platforms,
            and infrastructure tooling on my own. That grind landed me <strong>5 job offers</strong> and set the
            foundation for everything that followed.
        </p>
        <p>
            With <strong>13+ years of hands-on experience</strong> across AWS, GCP, and Azure, I now work as a
            Senior DevOps Engineer. Along the way I grew my salary <strong>2.5x</strong> through deliberate
            career moves — and documented the entire journey so others could learn from it.
        </p>
        <p>
            In 2024 I launched <strong>LivingDevOps</strong> to pass on what I wish someone had taught me earlier.
            The platform runs intensive, <strong>80% hands-on</strong> bootcamps in AWS, Azure, and GCP, and I've
            personally mentored over <strong>800 professionals</strong> into DevOps careers through bootcamps,
            one-on-one sessions, and mock interviews.
        </p>
    </div>
</section>

<!-- Skills -->
<section id="skills">
    <div class="divider"></div>
    <h2 class="section-title">Skills &amp; Tools</h2>
    <p class="section-sub">The tech stack I work with daily</p>
    <div class="skills-grid">
        <div class="skill-card">
            <h4>Cloud Platforms</h4>
            <div class="tag-row">
                <span class="tag">AWS</span>
                <span class="tag">GCP</span>
                <span class="tag">Azure</span>
            </div>
        </div>
        <div class="skill-card">
            <h4>Infrastructure as Code</h4>
            <div class="tag-row">
                <span class="tag">Terraform</span>
                <span class="tag">Ansible</span>
                <span class="tag">Packer</span>
                <span class="tag">Kustomize</span>
            </div>
        </div>
        <div class="skill-card">
            <h4>Containers &amp; Orchestration</h4>
            <div class="tag-row">
                <span class="tag">Docker</span>
                <span class="tag">Kubernetes</span>
                <span class="tag">EKS</span>
                <span class="tag">Helm</span>
                <span class="tag">ArgoCD</span>
            </div>
        </div>
        <div class="skill-card">
            <h4>CI / CD</h4>
            <div class="tag-row">
                <span class="tag">GitHub Actions</span>
                <span class="tag">Jenkins</span>
                <span class="tag">Tekton</span>
            </div>
        </div>
        <div class="skill-card">
            <h4>Monitoring &amp; Security</h4>
            <div class="tag-row">
                <span class="tag">Prometheus</span>
                <span class="tag">Grafana</span>
                <span class="tag">Vault</span>
                <span class="tag">Keycloak</span>
                <span class="tag">DevSecOps</span>
            </div>
        </div>
        <div class="skill-card">
            <h4>Scripting &amp; Serverless</h4>
            <div class="tag-row">
                <span class="tag">Python</span>
                <span class="tag">Bash</span>
                <span class="tag">AWS Lambda</span>
                <span class="tag">Serverless</span>
            </div>
        </div>
    </div>
</section>

<!-- Projects -->
<section id="projects">
    <div class="divider"></div>
    <h2 class="section-title">Open Source Projects</h2>
    <p class="section-sub">Hands-on resources built for the community</p>
    <div class="projects-grid">
        <a href="https://github.com/akhileshmishrabiz/devops-zero-to-hero" class="project-card" target="_blank">
            <h4>devops-zero-to-hero</h4>
            <p>End-to-end DevOps learning path with real-world projects and automation scripts.</p>
            <span class="stars">&#9733; 394 stars</span>
        </a>
        <a href="https://github.com/akhileshmishrabiz/kubernetes-zero-to-hero" class="project-card" target="_blank">
            <h4>kubernetes-zero-to-hero</h4>
            <p>Kubernetes from fundamentals to production-grade EKS cluster setups.</p>
            <span class="stars">&#9733; 37 stars</span>
        </a>
        <a href="https://github.com/akhileshmishrabiz/practice-devops" class="project-card" target="_blank">
            <h4>practice-devops</h4>
            <p>Curated hands-on DevOps exercises to sharpen real skills.</p>
            <span class="stars">&#9733; 30 stars</span>
        </a>
        <a href="https://github.com/akhileshmishrabiz/toffee-terraform-wrapper" class="project-card" target="_blank">
            <h4>toffee-terraform-wrapper</h4>
            <p>A Terraform tooling wrapper to simplify IaC workflows.</p>
            <span class="stars">&#9733; 12 stars</span>
        </a>
    </div>
</section>

<!-- Writing -->
<section id="writing">
    <div class="divider"></div>
    <h2 class="section-title">Writing &amp; Content</h2>
    <p class="section-sub">Teaching DevOps through real-world stories</p>
    <div class="writing-grid">
        <a href="https://medium.com/@akhilesh-mishra" class="writing-card" target="_blank">
            <div class="platform-badge">Medium &middot; 17K+ Followers</div>
            <h4>Living DevOps Publication</h4>
            <p>In-depth articles on Docker, Terraform, IAM, and career growth in DevOps.</p>
        </a>
        <a href="https://akhileshmishra.substack.com" class="writing-card" target="_blank">
            <div class="platform-badge">Substack &middot; 4K+ Subscribers</div>
            <h4>DevOps with Akhilesh</h4>
            <p>Weekly newsletter: real projects, industry insights, and curated job opportunities.</p>
        </a>
        <a href="https://dev.to/livingdevops" class="writing-card" target="_blank">
            <div class="platform-badge">DEV Community</div>
            <h4>Technical Deep-Dives</h4>
            <p>Tutorials on Terraform, GitHub Actions OIDC, Docker build optimization, and more.</p>
        </a>
        <a href="https://livingdevops.com" class="writing-card" target="_blank">
            <div class="platform-badge">LivingDevOps &middot; Bootcamps</div>
            <h4>AWS / Azure / GCP Bootcamps</h4>
            <p>Intensive, hands-on bootcamps — 80% practice, real production scenarios.</p>
        </a>
    </div>
</section>

<!-- Connect -->
<section id="connect">
    <div class="divider"></div>
    <h2 class="section-title">Connect</h2>
    <p class="section-sub">Let's stay in touch</p>
    <div class="connect-grid">
        <a href="https://in.linkedin.com/in/akhilesh-mishra-0ab886124" class="connect-card" target="_blank">
            <span class="icon">&#128188;</span> LinkedIn
        </a>
        <a href="https://github.com/akhileshmishrabiz" class="connect-card" target="_blank">
            <span class="icon">&#128196;</span> GitHub
        </a>
        <a href="https://x.com/livingdevops" class="connect-card" target="_blank">
            <span class="icon">&#128227;</span> X (Twitter)
        </a>
        <a href="https://medium.com/@akhilesh-mishra" class="connect-card" target="_blank">
            <span class="icon">&#9744;</span> Medium
        </a>
        <a href="https://akhileshmishra.substack.com" class="connect-card" target="_blank">
            <span class="icon">&#9993;</span> Substack
        </a>
        <a href="https://topmate.io/akhilesh_mishra" class="connect-card" target="_blank">
            <span class="icon">&#128197;</span> Topmate
        </a>
        <a href="https://livingdevops.com" class="connect-card" target="_blank">
            <span class="icon">&#127891;</span> LivingDevOps
        </a>
        <a href="https://dev.to/livingdevops" class="connect-card" target="_blank">
            <span class="icon">&#128189;</span> DEV Community
        </a>
    </div>
</section>

<!-- Footer -->
<footer>
    <p>&copy; 2026 Akhilesh Mishra &middot; <a href="https://livingdevops.com">livingdevops.com</a> &middot; Built with Flask &amp; Python</p>
</footer>






</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(TEMPLATE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
