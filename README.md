# Radish bdd extensions

Python packages collection for tests automation simplification with [radish-bdd](https://github.com/radish-bdd/radish) library

## radish_ext

Package provides:
* config mechanism based on yaml files
* python logging configuration
* test data class
* with data replacement
    * allow to use ${cfg.section.attribute} in steps arguments
* step_config
* class to store step configuration
* shared in single context

## radish_rest

Package provides:
* requests base steps
* requests steps config
* request test data
    * share test data related to rest
        * request response
        * request body
* request tools
    * request logging
    
## radish_selenium

Package provides
* selenium base steps
* selenium steps config
    * selenium web driver factory
* selenium hooks
    * failure
        * attach html/screenshots in case
    * web browser close
* selenium test data
    * to store current page objects in context