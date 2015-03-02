# Learning Puppet — Templates

  1. Begin
  2. Stopping the Static Content Explosion
  3. Template Files
  4. Rendering Templates
    1. Refererring to Template Files in Modules
    2. Inline Templates
    3. Aside: Functions in General
  5. Variables in Templates
  6. The ERB Templating Language
    1. Non-Printing Tags
    2. Printing an Expression
    3. Comments
    4. Suppressing Line Breaks and Leading Space
  7. An Example: NTP Again
    1. Adjusting the Manifest
    2. Editing the Templates
  8. Next

## Begin

Let’s make a small adjustment to our NTP module from the last chapter: remove the `source` attribute from the file resource, and replace it with a `content` attribute using a new function. (Remember that `source` specifies file contents as a file, and `content` specifies file contents as a **string.**)
    
    
        # /etc/puppetlabs/puppet/modules/ntp/manifests/init.pp
    
        class ntp {
          #...
          #...
          #...
          file { 'ntp.conf':
            path    => '/etc/ntp.conf',
            ensure  => file,
            require => Package['ntp'],
            content => template("ntp/${conf_file}.erb"),
          }
        }
    

Then, copy the config files into the templates directory:
    
    
    # cd /etc/puppetlabs/puppet/modules/ntp
    # mkdir templates
    # cp files/ntp.conf.el templates/ntp.conf.el.erb
    # cp files/ntp.conf.debian templates/ntp.conf.debian.erb
    

The module should work the same way it’s been working, but your config files are no longer static files; they’re templates.

## Stopping the Static Content Explosion

So consider our NTP module.

Right now, we’re shipping around two different config files, which resemble the defaults for Red Hat-like and Debian-like OSes. What if we wanted to make a few small and reasonable changes? For example:

  * Use different NTP servers for a small number of machines
  * Adjust the settings on virtual machines, so NTP doesn’t panic if the time jumps

We could end up maintaining eight or more different config files! Let’s not do that. Instead, we can manage a bunch of small differences in one or two **template** files.

Templates are documents that contain a mixture of _static_ and _dynamic_ content. By using a small amount of conditional logic and variable interpolation, they let you maintain one source document that can be rendered into any number of final documents.

For more details on the behavior of Puppet templates, see [the guide for Using Puppet Templates](/guides/templating.html); we’ll cover the basics right here.

## Template Files

Templates are saved as files with the .erb extension, and should be stored in the `templates/` directory of any module. There can be any number of subdirectories inside `templates/`.

## Rendering Templates

To use a template, you have to **render** it to produce an output string. To do this, use Puppet’s built-in `[template` function](/references/stable/function.html#template). This function takes a path to one or more template files and returns an output string:
    
    
        file {'/etc/foo.conf':
          ensure  => file,
          require => Package['foo'],
          content => template('foo/foo.conf.erb'),
        }
    

Notice that we’re using the output string as the value of the `content` attribute — it wouldn’t work with the `source` attribute, which expects a URL rather than the actual content for a file.

### Refererring to Template Files in Modules

The `template` function expects file paths to be in a specific format:

`<MODULE NAME>/<FILENAME INSIDE TEMPLATES DIRECTORY>`

That is, `template('foo/foo.conf.erb')` would point to the file `/etc/puppetlabs/puppet/modules/foo/templates/foo.conf.erb`.

> Note that the path to the template doesn’t use the same semantics as the path in a `puppet:///` URL. Sorry about the inconsistency.

### Inline Templates

Alternately, you can use [the `inline_template` function](/references/stable/function.html#inlinetemplate), which takes a string containing a template and returns an output string.

This is less frequently useful, but if you have a very small template, you can sometimes embed it in the manifest instead of making a whole new file for it.

> ### Aside: Functions in General
> 
> We’ve seen several functions already, including `include`, `template`, `fail`, and `str2bool`, so this is as good a time as any to explain what they are.
> 
> Puppet has two kinds of functions:
> 
>   * Functions that return a value
>   * Functions that do something else, without returning a value
> 
> The `template` and `str2bool` functions both return values; you can use them anywhere that requires a value, as long as the return value is the right kind. The `include` and `fail` functions do something else, without returning a value — declare a class, and stop catalog compilation, respectively.
> 
> All functions are run during catalog compilation. This means they run on the puppet master, and don’t have access to any files or settings on the agent node.
> 
> Functions can take any number of arguments, which are separated by commas and can be surrounded by optional parentheses:
> 
> `function(argument, argument, argument)`
> 
> Functions are plugins, so many custom plugins are available in modules.
> 
> Complete documentation about functions are available at [the functions page of the Puppet reference manual](/puppet/latest/reference/lang_functions.html) and [the list of built-in functions](/references/stable/function.html).

## Variables in Templates

Templates are powerful because they have access to all of the Puppet variables that are present when the template is rendered.

  * **Facts, global variables,** and **local variables from the current scope** are available to a template as _Ruby instance variables_ — instead of Puppet’s `$` prefix, they have an `@` prefix. (e.g. `@fqdn, @memoryfree, @operatingsystem`, etc.)
  * Variables from other scopes can be accessed with the `scope.lookupvar` method, which takes a long variable name without the `$` prefix. (For example, `scope.lookupvar('apache::user')`.)

## The ERB Templating Language

Puppet doesn’t have its own templating language; instead, it uses ERB, a common Ruby-based template language. (The Rails framework uses ERB, as do several other projects.)

ERB templates mostly look like normal configuration files, with the occasional `<% tag containing Ruby code %>`. [The ERB syntax is documented here](/guides/templating.html#erb-template-syntax), but since tags can contain _any_ Ruby code, it’s possible for templates to get pretty complicated.

In general, we recommend keeping templates as simple as possible: we’ll show you how to print variables, do conditional statements, and iterate over arrays, which should be enough for most tasks.

### Non-Printing Tags

ERB tags are delimited by angle brackets with percent signs just inside. (There isn’t any HTML-like concept of opening or closing tags.)
    
    
        <% document = "" %>
    

Tags contain one or more lines of Ruby code, which can set variables, munge data, implement control flow, or… actually, pretty much anything, except for print text in the rendered output.

### Printing an Expression

For that, you need to use a printing tag, which looks like a normal tag with an equals sign right after the opening delimiter:
    
    
        <%= sectionheader %>
          environment = <%= gitrevision[0,5] %>
    

The value you print can be a simple variable, or it can be an arbitrarily complicated Ruby expression.

### Comments

A tag with a hash mark right after the opening delimiter can hold comments, which aren’t interpreted as code and aren’t displayed in the rendered output.
    
    
        <%# This comment will be ignored. %>
    

### Suppressing Line Breaks and Leading Space

Regular tags don’t print anything, but if you keep each tag of logic on its own line, the line breaks you use will show up as a swath of whitespace in the final file. Similarly, if you’re indenting for readability, the whitespace in the indent can mess up the format of the rendered output.

If you don’t like that, you can:

  * Trim line breaks by putting a hyphen directly before the closing delimiter
  * Trim leading space by putting a hyphen directly after the opening delimiter
    
    
        <%- document += thisline -%>
    

## An Example: NTP Again

Let’s make the templates in your NTP module a little more clever.

First, make sure you change the file resource to use a template, like we saw at the top of this page. You should also make sure you’ve copied the config files to the `templates/` directory and given them the .erb extension.

### Adjusting the Manifest

Next, we’ll move the default NTP servers out of the config file and into the manifest:
    
    
        # /etc/puppetlabs/puppet/modules/ntp/manifests/init.pp
    
        class ntp {
          case $operatingsystem {
            centos, redhat: {
              $service_name    = 'ntpd'
              $conf_file   = 'ntp.conf.el'
              $default_servers = [ "0.centos.pool.ntp.org",
                                   "1.centos.pool.ntp.org",
                                   "2.centos.pool.ntp.org", ]
            }
            debian, ubuntu: {
              $service_name    = 'ntp'
              $conf_file   = 'ntp.conf.debian'
              $default_servers = [ "0.debian.pool.ntp.org iburst",
                                   "1.debian.pool.ntp.org iburst",
                                   "2.debian.pool.ntp.org iburst",
                                   "3.debian.pool.ntp.org iburst", ]
            }
          }
    
          $_servers = $default_servers
    
          package { 'ntp':
            ensure => installed,
          }
    
          service { 'ntp':
            name      => $service_name,
            ensure    => running,
            enable    => true,
            subscribe => File['ntp.conf'],
          }
    
          file { 'ntp.conf':
            path    => '/etc/ntp.conf',
            ensure  => file,
            require => Package['ntp'],
            content => template("ntp/${conf_file}.erb"),
          }
        }
    

We’re storing the servers in an array, so we can show how to iterate within a template. Right now, we’re not providing the ability to change the list of servers, but we’re paving the way to do so in the next chapter.

### Editing the Templates

First, make each template use the `$_servers` variable to create the list of `server` statements:
    
    
        <%# /etc/puppetlabs/puppet/modules/ntp/templates/ntp %>
    
        # Managed by Class['ntp']
        <% @_servers.each do |this_server| -%>
        server <%= this_server %>
        <% end -%>
    
        # ...
    

What’s this doing?

  * Using a non-printing Ruby tag to start a loop. We reference the `$_servers` Puppet variable by the name `@_servers`, then call Ruby’s `each` method on it. Everything between `do |server| -%>` and the `<% end -%>` tag will be repeated for each item in the `$_servers` array, with the value of that array item being assigned to the temporary `this_server` variable.
  * Within the loop, we print the literal word `server`, followed by the value of the current array item.

This snippet will produce something like the following:
    
    
    # Managed by Class['ntp']
    server 0.centos.pool.ntp.org
    server 1.centos.pool.ntp.org
    server 2.centos.pool.ntp.org
    

Next, let’s use the `$is_virtual` fact to make NTP perform better if this is a virtual machine. At the top of the file, add this:
    
    
        <% if @is_virtual == "true" -%>
        # Keep ntpd from panicking in the event of a large clock skew
        # when a VM guest is suspended and resumed.
        tinker panic 0
    
        <% end -%>
    

Then, _below_ the loop we made for the server statements, add this (being sure to replace the similar section of the Red Hat-like template):
    
    
        <% if @is_virtual == "false" -%>
        # Undisciplined Local Clock. This is a fake driver intended for backup
        # and when no outside source of synchronized time is available.
        server 127.127.1.0 # local clock
        fudge 127.127.1.0 stratum 10
    
        <% end -%>
    

By using facts to conditionally switch parts of the config file on and off, we can easily react to the type of machine we’re managing.

## Next

**Next Lesson:**

We’ve already seen that classes should sometimes behave differently for different kinds of systems, and have used facts to make conditional changes to both manifests and templates.

Sometimes, though, facts aren’t enough — there are times when a human has to decide what makes a machine different, because that difference is a matter of _policy._ (For example, the difference between a test server and a production server.)

In these cases, we need to give ourselves a way to manually change the way a class works. We can do this by passing in data with [class parameters](./modules2.html).

**Off-Road:**

Are you managing any configuration on your real infrastructure yet? You’ve learned a lot by now, so why not [download Puppet Enterprise for free](http://info.puppetlabs.com/download-pe.html), follow [the quick start guide](/pe/latest/quick_start.html) to get a small environment installed, and start automating?

> ↑ Back to top

  * Docs Quick Nav

Home
    [Puppet Docs Front Page](/)
#1 Most Popular
    [The Resource Type Reference](/references/stable/type.html)
Puppet Enterprise
    [Puppet Enterprise User's Guide (latest)](/pe/latest/)
    [Quick Start Guide](/pe/latest/quick_start.html)
Puppet in General (PE & Open Source)
    [Puppet Reference Manual (latest)](/puppet/latest/reference)
    [Learning Puppet](/learning/)
    [Glossary of Puppet Terms](/references/glossary.html)
Open Source Puppet
    [Installing](/guides/install_puppet/pre_install.html)
    [Upgrading](/guides/install_puppet/upgrading.html)
Facter
    [Core Facts Reference](/facter/latest/core_facts.html)
    [Writing Custom Facts](/facter/latest/fact_overview.html)
PuppetDB
    [PuppetDB Manual](/puppetdb/latest)
MCollective
    [All MCollective Docs](/mcollective/index.html)
    [References](/mcollective/reference/index.html)
    [Writing Plugins](/mcollective/simplerpc/index.html)
  * [Introduction](/learning/index.html)
  * **Part one: Serverless Puppet**
    * [Resources and the RAL](/learning/ral.html)
    * [Manifests](/learning/manifests.html)
    * [Ordering](/learning/ordering.html)
    * [Variables, Conditionals, Facts](/learning/variables.html)
    * [Modules and Classes](/learning/modules1.html)
    * Templates
    * [Class Parameters](/learning/modules2.html)
    * [Defined Types](/learning/definedtypes.html)
  * **Part two: Master/Agent Puppet**
    * [Preparing an Agent VM](/learning/agentprep.html)
    * [Basic Agent/Master Puppet](/learning/agent_master_basic.html)
