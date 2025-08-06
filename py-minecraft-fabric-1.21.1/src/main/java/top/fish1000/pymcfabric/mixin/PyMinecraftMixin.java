package top.fish1000.pymcfabric.mixin;

import net.minecraft.server.MinecraftServer;
import net.minecraft.util.profiler.Profiler;

import py4j.GatewayServer;

import top.fish1000.pymcfabric.Utils;
import top.fish1000.pymcfabric.Py4jEntryPoint;
import top.fish1000.pymcfabric.executor.NamedAdvancedExecutor;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(MinecraftServer.class)
public abstract class PyMinecraftMixin {

    @Shadow
    public Profiler profiler;

    @Shadow
    public int ticks;

    // public final NamedExecutor<MinecraftServer> executor = new NamedExecutor<>(()
    // -> ticks);
    private final NamedAdvancedExecutor<MinecraftServer> executor = new NamedAdvancedExecutor<>(() -> ticks);

    private void startPy4j() {
        GatewayServer gatewayServer = new GatewayServer(new Py4jEntryPoint() {
            @Override
            public NamedAdvancedExecutor<MinecraftServer> getExecutor() {
                return PyMinecraftMixin.this.executor;
            }
        });
        gatewayServer.start();
    }

    @Inject(at = @At("HEAD"), method = "loadWorld()V")
    private void init(CallbackInfo info) {
        try {
            startPy4j();
        } catch (Exception e) {
            Utils.LOGGER.error("Failed to start py4j server", e);
            return;
        }
        Utils.LOGGER.info("Py4j server started successfully");
    }

    @Inject(at = @At(value = "INVOKE", target = "Lnet/minecraft/server/function/CommandFunctionManager;tick()V", shift = At.Shift.AFTER), method = "tickWorlds()V")
    private void tick(CallbackInfo info) {
        profiler.swap("py4j");
        // long start = System.nanoTime();
        executor.tick((MinecraftServer) (Object) this, "tick");
        // long end = System.nanoTime();
        // utils.LOGGER.info("py4j tick: {}ms", (end - start) / 1000000d);
    }
}
