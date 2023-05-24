# Common Plugin Controller
Python based Common Plugin Controller.
A Plugin Controller can be used to manage commonly structured plugins for project-specific purposes.

## Usage
A Plugin Controller object can be instantiated from the Common Plugin Controller class (located in 
common_plugin_controller.py), given a dictionary, containing 
- the supported plugin types as key and its class as value ('plugin_class_dictionary')
- a list of folders, containing plugins which are represented by folders themselves ('plugin_folders')
  - if not declared, only the local plugin folder ('plugins') is checked
- a list of supported types, limiting the types, handled by the instance ('supported_types')
  - can be used to distribute load or responsibility among multiple controller instances 
  - if not declared, all types are handled

Once initiated, a Plugin Controller instance offers the following functionality:
- reload(): Plugins are reloaded, based on the current controller parameters
- reload_from_path(path): Reload plugins, located under the given path
- dynamically_load_plugin_folder(plugin_folder): Load in plugins from the given plugin folder
  - dynamically loaded content is cached and reloaded when using reload()
- dynamically_load_plugin(plugin_path): Load in a single plugin, declared by the given path
  - dynamically loaded content is cached and reloaded when using reload()
- save_plugin_info(plugin_type, plugin_name): Save plugin info back to disk
  - the target plugins can be limited by declaring plugin type, plugin name or both
  - if no type or name is given, all plugin info profiles are saved back to disk
- get_plugin(plugin_type, plugin_name): Method for acquiring plugin by type and name

Note, that plugins can also be acquired by directly accessing the Plugin Controllers 'plugins'-instance variable.
It holds a nested dictionary containing a specific plugin instance under its type as first key and name as second key. 

## Plugin Type Class
Before specific plugins can be defined, a class needs to be implemented, representing plugins of this type.
Plugin classes should inherit from the GenericPlugin class (located in /model/plugins.py).
Additional structural parameters should be validated in its '__init__'-method and PluginImportExceptions 
(located in /model/exceptions.py) should be raised in case of missing or invalid parameters.
Plugin classes should also implement simplistic handle-methods, interfacing more complex functionality.

## Plugin
A plugin is represented as a folder, containing an 'info.json'-file and additional files if necessary.
The 'info.json'-file should contain a 'type'-value, defining the plugin type and a 'name'-value defining a unique
name.
