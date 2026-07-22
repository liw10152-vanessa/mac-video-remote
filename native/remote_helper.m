// Copyright © 2026 liw10152-vanessa. All rights reserved.
// Personal-use permission is described in LICENSE.md.
#import <AppKit/AppKit.h>
#import <ApplicationServices/ApplicationServices.h>
#import <Foundation/Foundation.h>
#import <signal.h>
#import <unistd.h>

static volatile sig_atomic_t keepRunning = 1;

static void stopHolding(int signalNumber) {
    (void)signalNumber;
    keepRunning = 0;
}

static CGEventFlags parseFlags(NSString *value) {
    CGEventFlags flags = 0;
    if ([value containsString:@"shift"]) flags |= kCGEventFlagMaskShift;
    if ([value containsString:@"command"]) flags |= kCGEventFlagMaskCommand;
    if ([value containsString:@"option"]) flags |= kCGEventFlagMaskAlternate;
    if ([value containsString:@"control"]) flags |= kCGEventFlagMaskControl;
    return flags;
}

static void postKey(CGKeyCode key, bool down, bool autorepeat, CGEventFlags flags) {
    CGEventSourceRef source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState);
    CGEventRef event = CGEventCreateKeyboardEvent(source, key, down);
    CGEventSetFlags(event, flags);
    CGEventSetIntegerValueField(event, kCGKeyboardEventAutorepeat, autorepeat ? 1 : 0);
    CGEventPost(kCGHIDEventTap, event);
    CFRelease(event);
    CFRelease(source);
}

static int printState(void) {
    NSRunningApplication *app = NSWorkspace.sharedWorkspace.frontmostApplication;
    NSDictionary *state = @{
        @"appName": app.localizedName ?: @"未知 App",
        @"bundleIdentifier": app.bundleIdentifier ?: @"unknown",
        @"accessibilityTrusted": @(AXIsProcessTrusted())
    };
    NSData *data = [NSJSONSerialization dataWithJSONObject:state options:0 error:nil];
    fwrite(data.bytes, 1, data.length, stdout);
    fputc('\n', stdout);
    return 0;
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc < 2) {
            fprintf(stderr, "usage: remote-helper state|prompt|tap|hold ...\n");
            return 2;
        }
        NSString *command = [NSString stringWithUTF8String:argv[1]];

        if ([command isEqualToString:@"state"]) return printState();
        if ([command isEqualToString:@"prompt"]) {
            const void *keys[] = { kAXTrustedCheckOptionPrompt };
            const void *values[] = { kCFBooleanTrue };
            CFDictionaryRef options = CFDictionaryCreate(NULL, keys, values, 1,
                                                          &kCFTypeDictionaryKeyCallBacks,
                                                          &kCFTypeDictionaryValueCallBacks);
            bool trusted = AXIsProcessTrustedWithOptions(options);
            CFRelease(options);
            return trusted ? 0 : 1;
        }
        if (argc < 3) return 2;

        CGKeyCode key = (CGKeyCode)strtoul(argv[2], NULL, 10);
        CGEventFlags flags = argc >= 4 ? parseFlags([NSString stringWithUTF8String:argv[3]]) : 0;
        if ([command isEqualToString:@"tap"]) {
            postKey(key, true, false, flags);
            usleep(25000);
            postKey(key, false, false, flags);
            return 0;
        }
        if ([command isEqualToString:@"hold"]) {
            signal(SIGTERM, stopHolding);
            signal(SIGINT, stopHolding);
            postKey(key, true, false, flags);
            usleep(280000);
            while (keepRunning) {
                postKey(key, true, true, flags);
                usleep(75000);
            }
            postKey(key, false, false, flags);
            return 0;
        }
        return 2;
    }
}
