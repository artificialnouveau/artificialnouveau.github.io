# frozen_string_literal: true

source "https://rubygems.org"
gemspec

# Pin sass-embedded to a version with reliable prebuilt binaries. Newer releases
# (e.g. 1.100.0) fall back to compiling the native extension on the GitHub Pages
# runner and fail "bundle install" (exit 5), breaking the Jekyll deploy. This
# satisfies jekyll-sass-converter 3.x's "sass-embedded ~> 1.54" requirement.
gem "sass-embedded", "1.69.5"
