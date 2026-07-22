# Security Policy

## Supported version

Security fixes are applied to the latest code on the default branch.

## Threat model

Mac Video Remote is designed for a trusted home or personal local network. It is not designed to be exposed to the public internet, forwarded through a router, or used on an untrusted shared network.

The pairing code authorizes playback-control actions. Anyone who obtains the code while the service is running may be able to send those actions from the same reachable network.

## Safe use

- Run the service only on a trusted Wi-Fi network.
- Never publish a URL containing the pairing code.
- Do not configure router port forwarding for port `8765`.
- Stop the terminal process when remote control is no longer needed.
- Keep macOS updated and grant Accessibility permission only to trusted applications.
- Reset a compromised pairing code by stopping the service, removing the local pairing-code file, and starting the service again.

Pairing-code location:

```text
~/Library/Application Support/MacVideoRemote/pairing-code
```

## Reporting a vulnerability

Use GitHub’s private vulnerability reporting feature if it is available for this repository. Do not post pairing codes, proof-of-concept control URLs, or private network details in a public Issue.

Include the affected version, impact, reproduction conditions, and a suggested mitigation if known. Please allow reasonable time for investigation before public disclosure.
