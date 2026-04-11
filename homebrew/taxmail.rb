# Homebrew Cask — pre-built app, zero compilation needed
# Put this file in your tap repo: homebrew-taxmail/Casks/taxmail.rb
# User installs with: brew install --cask Franklinwang72/taxmail/taxmail

cask "taxmail" do
  version "0.1.0"
  sha256 "REPLACE_AFTER_UPLOAD"

  url "https://github.com/Franklinwang72/taxmail/releases/download/v#{version}/Taxmail-v#{version}.zip"
  name "Taxmail"
  desc "Render LaTeX formulas for email"
  homepage "https://github.com/Franklinwang72/taxmail"

  depends_on macos: ">= :ventura"

  app "Taxmail.app"

  postflight do
    # Ensure Python venv exists
    system_command "/bin/bash", args: [
      "-c",
      "cd '#{staged_path}' && if [ -f setup_venv.sh ]; then ./setup_venv.sh; fi"
    ]
  end

  zap trash: [
    "~/.config/latex2clip",
    "~/Library/Caches/taxmail",
  ]

  caveats <<~EOS
    Taxmail requires Python 3.10+ and pip:
      brew install python@3.12

    After installation, run once to set up:
      open /Applications/Taxmail.app

    For full LaTeX support (complex formulas), install MacTeX:
      brew install --cask mactex-no-gui
  EOS
end
