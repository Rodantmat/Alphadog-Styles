# Production assets (branch prod-assets of Alphadog-Styles)
Restore in a fresh session (repo already cloned at ~/alphadog-styles):
  git clone --depth 1 -b prod-assets https://github.com/Rodantmat/Alphadog-Styles.git /tmp/assets
  cd /tmp/assets && for z in merch_lib backgrounds kl_engine media_extra; do cat $z.zip.part_* > /tmp/$z.zip; done
  cd <repo>/out && unzip -qo /tmp/merch_lib.zip && unzip -qo /tmp/backgrounds.zip && unzip -qo /tmp/media_extra.zip
  cd /tmp && unzip -qo /tmp/kl_engine.zip      # creates /tmp/kl (engine deps, bgc backgrounds)
