
title='Learning Puppet -- Resources and the RAL'
description='Welcome to Learning Puppet! This series covers the basics of writing Puppet code and using Puppet Enterprise. You should already have a copy of the Learning Puppet VM; if you don\'t, you can download it for free.'
homepage = "https://docs.puppetlabs.com/learning/ral.html"

template = """
{
  "olpVersion": "0.1",
  "name": "puppet-ral",
  "version": "1.1.0",
  "title": "%s",
  "description": "%s",
  "type": "module",
  "labels": [
    "puppet"
  ],
  "git": "http://github.com/outlearn/",
  "homepage": "%s",
  "authors": [
    {
      "name": "Will Koffel",
      "email": "will@outlearn.com",
      "twitter": "willk"
    }
  ]
  "organization": "Super Mega Corp, Inc.",
  "license": "public",
  "credits": [
    "Linux Torvalds",
    "Funding provided by the Acme Foundation"
  ],
  "contact" : {
    "email": "courses-feedback@supermegacorp.com"
  }
  "changes": [
    "fixed some typos in the original content",
    "added more details on git branching strategies"
  ],
  "learningPath": true,
  "parts": [
    {
      "type": "asset",
      "contentType": "text/markdown",
      "location": "assets/outlearn-intro.md",
    },
    {
      "type": "asset",
      "contentType": "video/youtube",
      "url": "https://www.youtube.com/watch?v=YPaz0p2dpEk",
    }
}
"""%(title, description, homepage,)

print template
