# © 2019 Nokia

# Licensed under the BSD 3 Clause license
# SPDX-License-Identifier: BSD-3-Clause

@feature_radish_rest
@auto
Feature: radish_rest test for based requests tests
  Used for base requests tests

  @test_rest1
  Scenario: radish_rest get request
    When request "r1" is sent to url "https://petstore.swagger.io/v2/pet/findByStatus?status=available" by a http client with "GET" method
    Then response code for request "r1" is 200

  @test_rest2
  Scenario: radish_rest get request to url read from user config yaml
#     The url parameter can be replaced based on user config yaml
#     the cfg contains section Swagger with url attribute
    When request "r1" is sent to url "${cfg.Swagger.url}/findByStatus?status=available" by a http client with "GET" method
    Then response code for request "r1" is 200
