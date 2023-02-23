# Ansible Collection - dandyrow.stow

**The contents of this collection is moving to the [dandyrow.iac](https://github.com/dandyrow/dandyrow.iac) collection**

This collection will be **depricated** in the next release.

This change is being made due to unforseen ways Ansible handles collection and role dependencies. The new collection, [dandyrow.iac](https://github.com/dandyrow/dandyrow.iac), will have a wider purpose above and beyond using stow with Ansible.

The most recent changes to the module contained within this collection have been backported here but from now this collection no longer receive feature, maintenance or security updates, please switch to the [dandyrow.iac](https://github.com/dandyrow/dandyrow.iac) collection, version 1.0.0 of which contains a feature compatible version of the stow module contained within this collection.

This collection is for the stow module which allows Ansible to interact with the GNU stow symlink manager.

I decided to create this module as I wanted to automate the deployment of my dotfiles on Linux systems and they are organised into packages which can be installed using GNU stow. Dotfiles repo can be found [here](https://github.com/dandyrow/dotfiles) if you're interested.

Documentation for this module is hosted on GitHub Pages and is available [here](https://dandyrow.github.io/ansible-collection-stow/).

You can find the Ansible Galaxy page for this collection [here](https://galaxy.ansible.com/dandyrow/stow).
