@feature_radish_selenium
Feature: Examples for radish_selenium
  This feature shows the base selenium tests with radish_selenium
  The user provides yaml configuration file
    --user-data "cfg=ui_conf.yaml"
  Based on user yaml selenium driver is created


  @auto
  @test_sel1
  Scenario: radish_selenium open url
    When open url "https://nokia.com" in a web browser
    Then page title contains "Nokia"

  @auto
  @test_sel2
  Scenario: radish_selenium open url read from user config yaml
#     The url parameter can be replaced based on user config yaml
#     the cfg contains section Nokia with url attribute
    When open url "${cfg.Nokia.url}" in a web browser
    Then page title contains "Nokia"
