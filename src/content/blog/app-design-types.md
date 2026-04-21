---
title: "Two Ways to Build a Web App (and What You’re Actually Choosing)"
description: "Most applications boil down to server-rendered or API-driven designs. The difference isn’t just technical, it shapes how your system evolves."
publishDate: 2026-03-22
draft: false
tags: ["data-engineering", "application-architecture", "web-development", "api-design", "backend", "frontend"]
---

There are a lot of ways to build applications.

But if you zoom out far enough, most of them collapse into two camps.

Server rendered, and API driven.

Everything else is just flavor, tooling, and how much JavaScript you’re willing to tolerate on a given day.

Server side rendering is the older model, and still one of the most straightforward. You run a web server. A user hits a route. The server returns HTML.

That HTML might be static, but more often it is generated dynamically using a template engine. In Python, that might be Flask with Jinja2 or Django’s templating system. In PHP, something like Laravel. You define routes, handle requests, and return fully formed pages.

The browser’s job is simple. Render what it is given.

There is something very honest about this model. The server owns the state. The server decides what the user sees. You can follow the flow from request to response without needing to mentally simulate a second application running in the browser.

It is also tightly coupled by design. Your backend and frontend are effectively the same thing. That can be a strength early on. It can become a constraint later.

The API driven model splits that world in two.

The backend still exposes routes, still handles methods like GET and POST, but instead of returning HTML, it returns data. JSON most of the time. Sometimes XML if you are feeling nostalgic or dealing with older systems.

The frontend becomes its own application. It is written in JavaScript, using frameworks like React or Vue or Angular. It calls the backend, gets data, and decides how to render it.

Now the browser is doing much more work. It is not just rendering. It is orchestrating.

This separation gives you flexibility. The same API can power a web app, a mobile app, and anything else that can speak HTTP. Teams can work independently. The system becomes more composable.

It also introduces a new class of problems. State is now shared across a boundary. You have to think about loading states, partial failures, versioning, and synchronization. What used to be one request and one response becomes a conversation.

## Where containerization fits into this

Containerization does not change these two models. It changes how you package and run them.

A container is just a way of saying this application, with exactly these dependencies, should run the same way everywhere. Whether that application is server rendered or API driven is almost incidental.

For a server rendered app, containerization usually means bundling the web server, the application code, and its runtime into a single unit. You build it once, run it anywhere, and scale it by spinning up more identical containers. It keeps the simplicity of the model while making deployment predictable.

For an API driven system, containers tend to reinforce the separation that already exists. The backend API runs in one container. The frontend might be served from another, or even from static hosting backed by a CDN. Each piece can be deployed, scaled, and versioned independently.

This is where things start to feel like architecture instead of just implementation.

You can scale your API without touching your frontend. You can deploy a new frontend without restarting your backend. You can introduce additional services without rewriting the entire system.

But containers also make it very easy to over-separate too early. What used to be one application can quickly turn into multiple services, each with its own deployment, logging, and failure modes.

The boundary between server rendered and API driven does not go away. Containers just make it easier to move that boundary around.

Used well, they give you consistency and flexibility.

Used poorly, they give you a distributed system before you needed one.

## The part that actually matters

Neither approach is strictly better.

Server rendered applications tend to be simpler to reason about and faster to get right. API driven systems tend to scale better across teams and platforms.

In practice, most systems end up somewhere in between.

Server rendered shells with API driven components layered in. APIs that return HTML fragments. Frontends that still rely on server side routing for critical paths.

The interesting part is not which one you choose. It is understanding what you are trading.

When you pick server rendering, you are choosing cohesion and simplicity.

When you pick API driven, you are choosing flexibility and separation.

Both are valid. Both can go very wrong.

The mistake is thinking the framework you chose made the decision for you.

It did not.

You are still the one deciding where the boundaries are.
