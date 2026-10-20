import Foundation
import Capacitor
import StoreKit

/// Bridges Apple's in-app review sheet to the web layer.
///
/// The web layer decides *whether* to ask (see `maybeAskForReview` in
/// www/app/index.html); this plugin only performs the ask. Apple throttles the
/// sheet to roughly three presentations per user per year and may show nothing
/// at all, so `requestReview` always resolves and never reports whether the
/// sheet actually appeared.
@objc(AppReviewPlugin)
public class AppReviewPlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "AppReviewPlugin"
    public let jsName = "AppReview"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "requestReview", returnType: CAPPluginReturnPromise)
    ]

    @objc func requestReview(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            guard let scene = self.bridge?.viewController?.view.window?.windowScene else {
                call.reject("No active window scene to present the review sheet in.")
                return
            }

            if #available(iOS 16.0, *) {
                AppStore.requestReview(in: scene)
            } else {
                SKStoreReviewController.requestReview(in: scene)
            }

            call.resolve()
        }
    }
}
